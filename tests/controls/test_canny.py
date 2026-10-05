"""Constructed CPU pixels only; these are not H3 or native Canny receipts."""
import os

import pytest

from kmin_video_director.contracts import ContractError, ControlSpec, MediaRef, SpatialTransform, digest_bytes
from kmin_video_director.contracts.worker import CancellationFlag, OperationContext, PreparedArtifact
from kmin_video_director.controls import canny
from kmin_video_director.controls.canny import BACKEND_ID, VERSION, build_control, thresholds
from tests.contracts.example_data import control, media, spatial


def prepared(tmp_path, frame, *, n=124, width=32, height=32):
    transform = spatial()
    transform.update(coded_width=width, coded_height=height, display_width=width, display_height=height,
                     fitted_width=width, fitted_height=height, canvas_width=width, canvas_height=height,
                     output_width=width, output_height=height)
    transform['content_rect'] = dict(x=0, y=0, width=width, height=height)
    raw = frame * n
    path = tmp_path / 'prepared.rgb'
    path.write_bytes(raw)
    m = media('prepared-test', 'prepared_video')
    m.update(availability='available', error=None, locator={'scheme':'project_relative','path':'prepared.rgb'})
    m['fingerprint'].update(digest=digest_bytes(raw), byte_size=len(raw))
    m['probe']['video'].update(codec='kvd-rgb24', width=width, height=height, end_pts=n)
    return PreparedArtifact('win-test', MediaRef.from_dict(m), SpatialTransform.from_dict(transform), n)


def spec(**parameters):
    c = control()
    c['backend'].update(id=BACKEND_ID, version='source-daeb5e5',
                        parameters={'low_threshold':0.2,'high_threshold':0.4, **parameters})
    c['preprocess_version'] = VERSION
    return ControlSpec.from_dict(c)


def context(tmp_path):
    return OperationContext(tmp_path, CancellationFlag(), {})


def box(width=32, height=32):
    return bytes(channel for y in range(height) for x in range(width)
                 for channel in ([255]*3 if 8 <= x < 24 and 8 <= y < 24 else [0]*3))


def test_native_contour_optional(tmp_path):
    if os.environ.get('KVD_RUN_NATIVE_CANNY_CPU') != '1':
        pytest.skip('NOT PERFORMED: native Comfy/Torch/Kornia execution is a separate CPU validation gate.')
    result = canny.native_canny_rgb(box(),32,32,.2,.4,canny.native_backend(),context=context(tmp_path))
    assert len(result) == 32*32*3 and set(result) == {0,255}
    pixels = [result[i:i+3] for i in range(0,len(result),3)]
    assert all(p in (b'\0\0\0', b'\xff\xff\xff') for p in pixels)
    assert 40 <= sum(p[0] != 0 for p in pixels) <= 140
    assert not any(pixels[y*32+x][0] for y in range(12,20) for x in range(12,20))
    assert not any(pixels[y*32+x][0] for y in range(4) for x in range(32))


def test_pipeline_restores_black_padding_without_exposing_bars(tmp_path,monkeypatch):
    # Stub native result: tests owned geometry plumbing, never Canny accuracy.
    monkeypatch.setattr(canny,'native_backend',lambda:(None,None,{'fixture':'synthetic'}))
    monkeypatch.setattr(canny,'native_canny_rgb',lambda frame,w,h,*a,**kw: bytes(w*h*3))
    p = prepared(tmp_path, bytes([255])*(32*32*3))
    s = p.spatial.to_dict()
    s.update(fitted_height=24, display_height=24, output_height=24)
    s['content_rect'] = dict(x=0,y=4,width=32,height=24)
    p = PreparedArtifact(p.window_id,p.media,SpatialTransform.from_dict(s),p.frame_count)
    artifact = build_control(p, spec(), context=context(tmp_path))
    assert artifact.frame_count == 124 and artifact.spatial_transform_id == p.spatial.id
    assert not any((tmp_path / artifact.media['locator']['path']).read_bytes())


@pytest.mark.parametrize('low,high', [(0,0.8),(-1,0.8),(0.8,0.4),(0.4,1),(float('nan'),0.8),(True,0.8)])
def test_threshold_domain_is_explicit(low, high):
    with pytest.raises(ContractError, match='INVALID_RECORD'):
        thresholds(low,high)


def test_pipeline_hashes_exact_geometry_and_ignores_strength(tmp_path,monkeypatch):
    monkeypatch.setattr(canny,'native_backend',lambda:(None,None,{'fixture':'synthetic'}))
    monkeypatch.setattr(canny,'native_canny_rgb',lambda frame,w,h,*a,**kw: bytes(w*h*3))
    p = prepared(tmp_path, box())
    first = build_control(p,spec(),context=context(tmp_path))
    raw = (tmp_path/first.media['locator']['path']).read_bytes()
    assert len(raw) == 124*32*32*3
    assert first.media['fingerprint']['digest'] == digest_bytes(raw)
    changed = spec().to_dict()
    changed['strength'] = 0.1
    second = build_control(p,ControlSpec.from_dict(changed),context=context(tmp_path))
    assert second.media['fingerprint']['digest'] == first.media['fingerprint']['digest']
    assert second.media['locator'] == first.media['locator']
    assert first.preview_media == first.media
    changed['backend']['parameters']['high_threshold'] = 0.6
    third = build_control(p,ControlSpec.from_dict(changed),context=context(tmp_path))
    assert third.media['locator'] != first.media['locator']


def test_off_is_explicit_and_creates_no_map(tmp_path):
    p = prepared(tmp_path, box())
    c = spec().to_dict()
    c.update(type='off', enabled=False)
    out = build_control(p,ControlSpec.from_dict(c),context=context(tmp_path))
    assert out.media is None and out.preview_media is None
    assert list(tmp_path.iterdir()) == [tmp_path/'prepared.rgb']


def test_changed_prepared_bytes_and_cancellation_are_rejected(tmp_path):
    p = prepared(tmp_path,box())
    (tmp_path/'prepared.rgb').write_bytes(bytes(124*32*32*3))
    with pytest.raises(ContractError, match='SOURCE_CHANGED'):
        build_control(p,spec(),context=context(tmp_path))
    c = context(tmp_path)
    c.cancellation.cancel()
    with pytest.raises(ContractError, match='CANCELLED'):
        build_control(p,spec(),context=c)
    assert not list(tmp_path.rglob('*.partial'))


def test_unavailable_native_backend_fails_instead_of_substitution(tmp_path,monkeypatch):
    def unavailable():
        raise ContractError('DEPENDENCY_MISSING','Native backend unavailable in this CPU fixture.')
    monkeypatch.setattr(canny,'native_backend',unavailable)
    with pytest.raises(ContractError,match='DEPENDENCY_MISSING'):
        build_control(prepared(tmp_path,box()),spec(),context=context(tmp_path))
    assert not list(tmp_path.rglob('*.rgb'))[1:]


@pytest.mark.parametrize('n', [1,123,125,346,362])
def test_window_size_is_bounded_before_open(tmp_path,n):
    p = prepared(tmp_path,box(),n=n)
    with pytest.raises(ContractError, match='FRAME_COUNT_MISMATCH'):
        build_control(p,spec(),context=context(tmp_path))
