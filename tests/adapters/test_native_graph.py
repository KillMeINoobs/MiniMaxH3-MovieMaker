"""Source/schema graph evidence only. No native model or sampler is executed."""
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import types

import pytest

from kmin_video_director.contracts import (ContractError, ControlSpec, GenerationWindow, MediaRef, RenderProfile,
                                         digest_bytes, digest_json, dumps)
from kmin_video_director.contracts.worker import (CancellationFlag, CompiledPrompt, ControlArtifact,
                                                NativeLink, NativeModelLinks, OperationContext)
from kmin_video_director.adapters.native_h3.graph import expand_native_render, generation_key
from kmin_video_director.adapters.native_h3.profile import validate_native_profile, schema_digest
from kmin_video_director.adapters.native_h3.components import COMPONENTS
from tests.contracts.example_data import control, media, profile, window

ROOT = Path(__file__).resolve().parents[2]
CORE = 'daeb5e53681e2b10a3f0727d9ec5bc90784bee10'


@pytest.fixture
def native_builder(monkeypatch):
    source = Path(os.environ.get('KVD_GRAPH_BUILDER_SOURCE',ROOT/'.ao/primary/daeb5e5/comfy_execution__graph_utils.py'))
    if not source.is_file():
        pytest.skip('Pinned stdlib-only native GraphBuilder source is not supplied. No substitute builder is used.')
    assert hashlib.sha256(source.read_bytes()).hexdigest() == 'dabb3f75952a1398891ed87ad853d4ea9c929f322ce6997d4ea916adbc2f209d'
    package = types.ModuleType('comfy_execution')
    package.__path__ = []
    spec = importlib.util.spec_from_file_location('comfy_execution.graph_utils',source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Inspected stdlib-only pinned GraphBuilder, never Comfy execution.
    monkeypatch.setitem(sys.modules,'comfy_execution',package)
    monkeypatch.setitem(sys.modules,spec.name,module)
    return module.GraphBuilder


def setup(tmp_path, *, off=False):
    capture = json.loads((ROOT/'tests/adapters/native_schema_fixture.json').read_text(encoding='utf-8'))
    schemas = deepcopy(capture['schemas'])
    names = {'model':'minimax_h3_ref2va_pruned_int8_convrot.safetensors',
             'clip':'qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors',
             'video_vae':'minimax_h3_video_vae_int8_convrot.safetensors',
             'audio_vae':'minimax_h3_audio_vae_fp32.safetensors',
             'patch':'minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors'}
    # Explicitly synthetic availability: the actual capture lacks the baseline base.
    p = profile()
    p.update(core_revision=CORE, memory_policy='one_window')
    p['components'] = {role:{'filename':name,'revision':'e5eb578a89295337b8ff433a035929ce0279e0b6',
                            'digest':{'algorithm':'sha256','hex':COMPONENTS[role][1]},'format':'comfy-native',
                            'metadata':{'adaln':'basis','time_embed_dim':8}} for role,name in names.items()}
    p['components']['model']['metadata'].update(family='ref2va',num_layers=50,video_channels=24)
    p['components']['patch']['metadata'].update(block_count=5,injection_layers=[0,10,20,30,40],
            input_channels=49,normalization_mode='pre_norm',metadata_adaln='adaln_basis',
            missing_keys=[],unexpected_keys=[])
    p['sampling'] = {'sampler_name':'res_multistep','scheduler':'simple','steps':20,
                     'denoise':1.0,'shift_video':12.0,'shift_audio':3.0}
    p['control_branch'] = {'version':'union-v1','block_count':5,'injection_layers':[0,10,20,30,40],
                          'input_channels':49,'adaln':'basis','normalization_mode':'pre_norm'}
    p['runtime'] = {'metadata_evidence':'synthetic CPU fixture; no weights loaded'}
    p['node_signatures'] = {name:schema_digest(schema) for name,schema in schemas.items()}
    w = window()
    w['compiled_prompt'] = w['resolved_settings']['prompt']
    w['extensions']['h3.test'] = {'spatial':{'canvas_width':32,'canvas_height':32}}
    c = control()
    if off:
        c.update(type='off',enabled=False)
    m = media('map-test','control_map')
    m['probe']['video'].update(width=32,height=32,end_pts=192)
    ca = ControlArtifact(w['id'],c['id'],None if off else MediaRef.from_dict(m),'space-1',192)
    prompt = CompiledPrompt(w['compiled_prompt'],digest_bytes(w['compiled_prompt'].encode('utf-8')),(),{})
    parent = {
        'base':{'class_type':'UNETLoader','inputs':{'unet_name':names['model'],'weight_dtype':'default'}},
        'clip':{'class_type':'CLIPLoader','inputs':{'clip_name':names['clip'],'type':'minimax','device':'default'}},
        'video-vae':{'class_type':'VAELoader','inputs':{'vae_name':names['video_vae']}},
        'audio-vae':{'class_type':'VAELoader','inputs':{'vae_name':names['audio_vae']}},
        'patch':{'class_type':'ModelPatchLoader','inputs':{'name':names['patch']}},
    }
    models = NativeModelLinks(*(NativeLink(id,0) for id in ('base','clip','video-vae','audio-vae','patch')))
    schema_path = tmp_path/'schemas.json'
    schema_path.write_text(json.dumps({'runtime':{'core_commit':CORE},'schemas':schemas}),encoding='utf-8')
    ctx = OperationContext(tmp_path,CancellationFlag(),{'native_schema_file':str(schema_path),
        'source_graph':json.dumps(parent),'control_spec_json':dumps(ControlSpec.from_dict(c)),
        'native_node_id':'expand-owner','canvas_width':'32','canvas_height':'32'})
    p = RenderProfile.from_dict(p)
    w['generation_key'] = generation_key(GenerationWindow.from_dict(w),p,ca,prompt,ControlSpec.from_dict(c))
    return GenerationWindow.from_dict(w),p,models,ca,prompt,ctx,schemas,parent


def test_real_builder_emits_native_nodes_correct_ports_and_empty_refs(tmp_path,native_builder):
    w,p,models,c,prompt,ctx,_,_ = setup(tmp_path)
    out = expand_native_render(w,p,models,c,prompt,None,context=ctx)
    nodes = {node['class_type']:node for node in out.graph.values()}
    condition = nodes['MiniMaxH3ReferenceToVideo']['inputs']
    assert condition['length'] == 192 and condition['width'] == condition['height'] == 32
    assert condition['prompt'] == prompt.text and condition['ref_image_size'] == 'match'
    assert not any(key.startswith('ref_') and key != 'ref_image_size' for key in condition)
    patch = nodes['MiniMaxH3FunControlNetApply']['inputs']
    assert patch['strength'] == 1 and patch['start_percent'] == 0 and patch['end_percent'] == 1
    assert 'source_video' not in patch and 'mask' not in patch
    assert nodes['RandomNoise']['inputs']['noise_seed'] == 18446744073709551615
    assert out.graph[out.images.node_id]['class_type'] == 'VAEDecode'
    assert out.graph[out.audio.node_id]['class_type'] == 'VAEDecodeAudio'
    assert out.graph[out.order_token.node_id]['class_type'] == 'KVD_NativeReceipt'
    assert out.graph_digest == digest_bytes(json.dumps(out.graph,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
    again = expand_native_render(w,p,models,c,prompt,None,context=ctx)
    assert again == out


def test_off_removes_only_structural_nodes_and_preserves_sampling(tmp_path,native_builder):
    on = setup(tmp_path)
    on_graph = expand_native_render(*on[:5],None,context=on[5]).graph
    off = setup(tmp_path,off=True)
    off_graph = expand_native_render(*off[:5],None,context=off[5]).graph
    on_by_type = {n['class_type']:n for n in on_graph.values()}
    off_by_type = {n['class_type']:n for n in off_graph.values()}
    assert set(on_by_type)-set(off_by_type) == {'KVD_ControlImage','MiniMaxH3FunControlNetApply'}
    for id in ('RandomNoise','MiniMaxH3ReferenceToVideo','KSamplerSelect','MiniMaxH3SigmaShift'):
        assert on_by_type[id] == off_by_type[id]


@pytest.mark.parametrize('fault',['missing_class','required_port','wrong_output','base_missing','unknown_profile','adaln','v2','metadata_keys','prompt','key','model_link'])
def test_source_and_metadata_mismatches_fail_before_native_expansion(tmp_path,native_builder,fault):
    w,p,models,c,prompt,ctx,schemas,parent = setup(tmp_path)
    pd = p.to_dict()
    if fault == 'missing_class': del schemas['MiniMaxH3SigmaShift']
    elif fault == 'required_port': schemas['BasicGuider']['input']['required']['mandatory_new'] = ['INT',{}]
    elif fault == 'wrong_output': schemas['VAEDecode']['output'] = ['LATENT']
    elif fault == 'base_missing': schemas['UNETLoader']['input']['required']['unet_name'][0].remove(pd['components']['model']['filename'])
    elif fault == 'unknown_profile': pd['core_revision'] = 'ff'*20
    elif fault == 'adaln': pd['components']['patch']['metadata']['time_embed_dim'] = 2688
    elif fault == 'v2': pd['control_branch']['version'] = 'union-v2'
    elif fault == 'metadata_keys': pd['components']['patch']['metadata']['unexpected_keys'] = ['control_blocks.5.after_proj.weight']
    elif fault == 'prompt': prompt = CompiledPrompt(prompt.text+'hidden',prompt.digest,(),{})
    elif fault == 'key': wd=w.to_dict(); wd['generation_key']=digest_bytes(b'stale'); w=GenerationWindow.from_dict(wd)
    elif fault == 'model_link': models=NativeModelLinks(NativeLink('base',1),models.clip,models.video_vae,models.audio_vae,models.patch)
    Path(ctx.versions['native_schema_file']).write_text(json.dumps({'runtime':{'core_commit':CORE},'schemas':schemas}),encoding='utf-8')
    with pytest.raises(Exception,match='MODEL_INCOMPATIBLE|STALE_DEPENDENCY|PROMPT_INVALID'):
        expand_native_render(w,RenderProfile.from_dict(pd),models,c,prompt,None,context=ctx)


def test_cancel_is_checked_before_schema_or_model_access(tmp_path,native_builder):
    w,p,models,c,prompt,ctx,_,_ = setup(tmp_path)
    ctx.cancellation.cancel()
    Path(ctx.versions['native_schema_file']).unlink()
    with pytest.raises(Exception,match='CANCELLED'):
        expand_native_render(w,p,models,c,prompt,None,context=ctx)


def test_actual_capture_does_not_certify_missing_baseline(tmp_path):
    _,p,_,_,_,_,_,_ = setup(tmp_path)
    capture_path = Path(os.environ.get('KVD_NATIVE_SCHEMA_CAPTURE',ROOT/'.ao/primary/native-schemas.json'))
    if not capture_path.is_file(): pytest.skip('No read-only native schema handoff supplied.')
    actual = json.loads(capture_path.read_text(encoding='utf-8-sig'))
    with pytest.raises(Exception,match='MODEL_INCOMPATIBLE'):
        validate_native_profile(p,actual['schemas'],actual['runtime']['core_commit'])


def test_review_h1_map_regeneration_and_relocation_preserve_content_identity(tmp_path):
    w,p,_,c,prompt,ctx,_,_=setup(tmp_path)
    spec=ControlSpec.from_dict(json.loads(ctx.versions['control_spec_json']))
    before=generation_key(w,p,c,prompt,spec)
    data=c.media.to_dict()
    data['fingerprint']['mtime_ns']='2'
    data['locator']['path']='relocated/map.rgb'
    relocated=ControlArtifact(c.window_id,c.control_spec_id,MediaRef.from_dict(data),c.spatial_transform_id,c.frame_count)
    assert generation_key(w,p,relocated,prompt,spec)==before
    data['fingerprint']['digest']=digest_bytes(b'different map bytes')
    changed=ControlArtifact(c.window_id,c.control_spec_id,MediaRef.from_dict(data),c.spatial_transform_id,c.frame_count)
    assert generation_key(w,p,changed,prompt,spec)!=before


@pytest.mark.parametrize('field,value',[('probe_version','native-recipe-next'),('decoder_version','rgb-next'),('video_stream',1)])
def test_effective_map_versions_and_stream_selection_invalidate_generation_key(tmp_path,field,value):
    w,p,_,c,prompt,ctx,_,_=setup(tmp_path)
    spec=ControlSpec.from_dict(json.loads(ctx.versions['control_spec_json']))
    data=c.media.to_dict()
    data['fingerprint'][field]=value
    if field=='video_stream': data['probe']['video']['stream_index']=value
    changed=ControlArtifact(c.window_id,c.control_spec_id,MediaRef.from_dict(data),c.spatial_transform_id,c.frame_count)
    assert generation_key(w,p,changed,prompt,spec)!=generation_key(w,p,c,prompt,spec)


def test_review_h2_unapproved_native_dtype_fails_before_expansion(tmp_path,native_builder):
    w,p,models,c,prompt,ctx,_,parent=setup(tmp_path)
    parent['base']['inputs']['weight_dtype']='fp8_e4m3fn'
    ctx=OperationContext(ctx.asset_root,ctx.cancellation,{**ctx.versions,'source_graph':json.dumps(parent)})
    with pytest.raises(ContractError,match='MODEL_INCOMPATIBLE'):
        expand_native_render(w,p,models,c,prompt,None,context=ctx)


@pytest.mark.parametrize('capture',[{}, {'schemas':{},'runtime':{}}, [], None, {'schemas':[], 'runtime':{'core_commit':CORE}}, {'schemas':{},'runtime':None}])
def test_review_h3_malformed_schema_envelope_fails_with_redacted_typed_error(tmp_path,capture):
    w,p,models,c,prompt,ctx,_,_=setup(tmp_path)
    Path(ctx.versions['native_schema_file']).write_text(json.dumps(capture),encoding='utf-8')
    with pytest.raises(ContractError,match='MODEL_INCOMPATIBLE') as error:
        expand_native_render(w,p,models,c,prompt,None,context=ctx)
    assert str(tmp_path) not in str(error.value)
