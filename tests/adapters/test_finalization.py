"""Constructed decoded RGB/PCM, real CPU encode/probe. Never H3 generation."""
import json
import os
from pathlib import Path

import pytest

from kmin_video_director.contracts import (ContractError, GenerationWindow, Project, SpatialTransform,
                                         digest_bytes, digest_json, resolve_project)
from kmin_video_director.contracts.worker import CancellationFlag, DecodedAV, OperationContext
from kmin_video_director.adapters.native_h3.finalize import finalize_window
from kmin_video_director.adapters.native_h3.order import DecodeReceipt, check_predecessor
from kmin_video_director.adapters.native_h3.media_bridge import decode_rgb
from tests.contracts.example_data import project, spatial, window


@pytest.fixture
def backend():
    paths = {'ffmpeg_path':os.environ.get('KVD_FFMPEG',''),'ffprobe_path':os.environ.get('KVD_FFPROBE','')}
    if not all(Path(p).is_file() for p in paths.values()):
        pytest.skip('Explicit existing FFmpeg/ffprobe paths are required for CPU synthetic I/O.')
    return paths


def setup(tmp_path,backend,*,audio_mode='preserve',ordinal=0):
    w = window()
    w['resolved_settings']['audio_mode'] = audio_mode
    w['resolved_settings_digest'] = digest_json(w['resolved_settings'])
    w = GenerationWindow.from_dict(w)
    s = spatial()
    s.update(coded_width=24,coded_height=16,display_width=24,display_height=16,
             fitted_width=24,fitted_height=16,canvas_width=32,canvas_height=32,
             output_width=24,output_height=16)
    s['content_rect'] = dict(x=4,y=8,width=24,height=16)
    s = SpatialTransform.from_dict(s)
    p = project()
    p['defaults']['audio_mode'] = audio_mode
    p['windows'] = {w.id:w.to_dict()}
    p['spatial_transforms'][s.id] = s.to_dict()
    p['audio_timeline'].update(mode=audio_mode)
    p = resolve_project(Project.from_dict(p))
    frames = tuple(bytes(c for y in range(32) for x in range(32)
                         for c in ([(index%180)+1,x,y] if index < 180 else [0,0,255])) for index in range(192))
    decoded = DecodedAV(frames,None,192,32,32)
    receipt = DecodeReceipt({'window_id':w.id,'generation_key':w['generation_key'],
        'project_id':p.project.id,'plan_revision':w['plan_revision'],'ordinal':w['ordinal'],
        'requested_frames':192,'width':32,'height':32,'profile_digest':digest_json(p.project['render_profiles'][w['render_profile_id']]),
        'prompt_digest':digest_bytes(w['compiled_prompt'].encode()),'native_graph_digest':digest_bytes(b'synthetic graph')},
        'synthetic_decoded')
    ctx = OperationContext(tmp_path,CancellationFlag(),{**backend,'evidence':'synthetic_decoded'})
    return decoded,w,p,s,receipt,ctx


def test_real_cpu_finalizer_crops_padding_trims_and_publishes_exact_receipt(tmp_path,backend):
    d,w,p,s,token,ctx = setup(tmp_path,backend)
    out = finalize_window(d,w,p,s,1,'request-test',token,context=ctx)
    r = out.result
    assert r['status'] == 'succeeded' and r['validation']['gpu'] == 'not_performed'
    assert r['validation']['evidence_kind'] == 'cpu_media'
    assert r['coverage']['requested_frames'] == r['coverage']['decoded_frames'] == 192
    assert r['coverage']['useful_frames'] == 180
    assert (r['coverage']['width'],r['coverage']['height']) == (24,16)
    for name in r['validation']['receipts']:
        assert json.loads((tmp_path/name).read_text())['evidence'] == 'synthetic_decoded'
    from kmin_video_director.contracts import MediaRef
    media = MediaRef.from_dict(r['artifacts'][0])
    pixels = tuple(decode_rgb(media,180,24,16,context=ctx))
    assert len(pixels) == 180 and pixels[0][:3] == bytes([1,4,8]) and pixels[-1][-3:] == bytes([180,27,23])
    check_predecessor(out.order_token,project_id=p.project.id,plan_revision=1,ordinal=1,useful_start=180)
    with pytest.raises(ContractError,match='PARTIAL_RESULT'):
        check_predecessor(token,project_id=p.project.id,plan_revision=1,ordinal=1,useful_start=180)


@pytest.mark.parametrize('fault',['count','geometry','extra','key','snapshot','prompt','attempt','cancel'])
def test_finalizer_rejects_unfinished_stale_or_cancelled_inputs_before_publish(tmp_path,backend,fault):
    d,w,p,s,t,ctx = setup(tmp_path,backend)
    attempt=1
    if fault=='count': d=DecodedAV(d.images,None,191,32,32)
    elif fault=='geometry': d=DecodedAV(d.images,None,192,64,32)
    elif fault=='extra': d=DecodedAV(d.images+(d.images[-1],),None,192,32,32)
    elif fault=='key': t=DecodeReceipt({**t.manifest,'generation_key':digest_bytes(b'stale')},t.origin)
    elif fault=='prompt': t=DecodeReceipt({**t.manifest,'prompt_digest':digest_bytes(b'hidden')},t.origin)
    elif fault=='snapshot': pd=p.project.to_dict(); pd['windows']={}; p=resolve_project(Project.from_dict(pd))
    elif fault=='attempt': attempt=0
    elif fault=='cancel': ctx.cancellation.cancel()
    with pytest.raises(ContractError):
        finalize_window(d,w,p,s,attempt,'request-test',t,context=ctx)
    assert not list(tmp_path.rglob('*.partial'))
    assert not list(tmp_path.rglob('*.json'))


def test_preserve_does_not_copy_generated_audio_or_shift_global_origin(tmp_path,backend):
    d,w,p,s,t,ctx = setup(tmp_path,backend)
    d = DecodedAV(d.images,{'unwanted':'must not be read'},d.frame_count,d.width,d.height)
    out=finalize_window(d,w,p,s,1,'request-audio',t,context=ctx)
    assert len(out.result['artifacts']) == 1
    assert out.result['audio']['mode'] == 'preserve'
    assert p.project['audio_timeline'] == project()['audio_timeline']


def test_disk_quota_failure_does_not_publish_success(tmp_path,backend):
    d,w,p,s,t,ctx = setup(tmp_path,backend)
    ctx=OperationContext(tmp_path,ctx.cancellation,{**ctx.versions,'disk_quota_bytes':'64'})
    with pytest.raises(ContractError,match='RESOURCE_LIMIT'):
        finalize_window(d,w,p,s,1,'quota',t,context=ctx)
    assert not list(tmp_path.rglob('*.partial'))


@pytest.mark.parametrize('key,value',[('disk_quota_bytes','invalid'),('timeout_seconds','nan'),
    ('timeout_seconds','inf'),('timeout_seconds','0')])
def test_invalid_resource_widgets_return_typed_errors_without_success(tmp_path,backend,key,value):
    d,w,p,s,t,ctx=setup(tmp_path,backend)
    ctx=OperationContext(tmp_path,ctx.cancellation,{**ctx.versions,key:value})
    with pytest.raises(ContractError,match='RESOURCE_LIMIT'):
        finalize_window(d,w,p,s,1,'invalid-budget',t,context=ctx)
    assert not list(tmp_path.rglob('*.partial')) and not list(tmp_path.rglob('*.json'))


def test_transport_graph_receipt_is_provenance_not_generation_cache_identity(tmp_path,backend):
    d,w,p,s,t,ctx=setup(tmp_path,backend)
    first=finalize_window(d,w,p,s,1,'same-attempt',t,context=ctx).result
    moved=DecodeReceipt({**t.manifest,'native_graph_digest':digest_bytes(b'relocated graph transport')},t.origin)
    second=finalize_window(d,w,p,s,1,'same-attempt',moved,context=ctx).result
    assert first.id==second.id and first['generation_key']==second['generation_key']
    assert first['artifacts'][0]['locator']==second['artifacts'][0]['locator']
    assert first['artifacts'][0]['fingerprint']['digest']==second['artifacts'][0]['fingerprint']['digest']
    assert first['provenance']['receipt_digest']!=second['provenance']['receipt_digest']
