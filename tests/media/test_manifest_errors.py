import json

import pytest

from kmin_video_director.contracts import MediaRef, GenerationWindow, SpatialTransform
from kmin_video_director.contracts.worker import ProjectLocator, StreamSelection
from kmin_video_director.errors import ContractError
from tests.media.support import context, video
from tests.assembly.support import prepared_project


def manifest_operation(root, envelope):
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    from kmin_video_director.media.probe import probe_media, probe_receipt_locator
    from kmin_video_director.media.prepare import prepare_window
    if envelope == 'source_timing':
        ctx = context(root)
        source = probe_media(ProjectLocator(video(root).name), StreamSelection(), context=ctx).media
        manifest = root / probe_receipt_locator(source)['path']
        return ctx, manifest, lambda selected_context: normalize_media(source, DEFAULT_RECIPE, context=selected_context)
    project, ctx = prepared_project(root, 6)
    canonical = MediaRef.from_dict(project['media'][project['canonical_media_id']])
    if envelope == 'normalization_cache':
        source = MediaRef.from_dict(project['media'][project['source_media_id']])
        return ctx, (root / canonical['locator']['path']).with_suffix('.json'), lambda selected_context: normalize_media(
            source, DEFAULT_RECIPE, context=selected_context)
    window = GenerationWindow.from_dict(next(iter(project['windows'].values())))
    spatial = SpatialTransform.from_dict(project['spatial_transforms'][window['spatial_transform_id']])
    prepared = prepare_window(window, canonical, spatial, context=ctx)
    return ctx, (root / prepared.media['locator']['path']).with_suffix('.json'), lambda selected_context: prepare_window(
        window, canonical, spatial, context=selected_context)


def file_bytes(root):
    # Only this test's tiny ordinary synthetic folder, with no source-folder scan.
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob('*') if path.is_file()}


@pytest.mark.parametrize('envelope', ['normalization_cache', 'preparation_cache', 'source_timing'])
@pytest.mark.parametrize('malformed', ['empty', 'list', 'scalar', 'nested', 'version'])
def test_malformed_owned_envelopes_are_typed_redacted_and_preserve_files(tmp_path, envelope, malformed):
    ctx, manifest, operation = manifest_operation(tmp_path, envelope)
    value = json.loads(manifest.read_text(encoding='utf-8'))
    if malformed == 'empty':
        value = {}
    elif malformed == 'list':
        value = []
    elif malformed == 'scalar':
        value = 7
    elif malformed == 'version':
        (value['normalization'] if envelope == 'normalization_cache' else value)['version'] = 'unsupported-owner-version'
    elif envelope == 'normalization_cache':
        value['normalization']['report'] = []
    elif envelope == 'preparation_cache':
        value['frame_count'] = 'six'
    else:
        value['final_frame_duration'] = []
    manifest.write_text(json.dumps(value), encoding='utf-8')
    before = file_bytes(tmp_path)
    with pytest.raises(ContractError) as raised:
        operation(ctx)
    assert raised.value.code == 'INVALID_RECORD'
    assert str(tmp_path) not in str(raised.value)
    assert str(tmp_path) not in json.dumps(raised.value.to_dict())
    assert file_bytes(tmp_path) == before


def test_manifest_failures_preserve_cancellation_and_json_size_limit_codes(tmp_path):
    ctx, manifest, operation = manifest_operation(tmp_path, 'normalization_cache')
    manifest.write_text('[]', encoding='utf-8')
    ctx.cancellation.cancel()
    with pytest.raises(ContractError) as raised:
        operation(ctx)
    assert raised.value.code == 'CANCELLED'
    # The existing bounded reader rejects size before parsing or envelope checks.
    manifest.write_bytes(b' ' * (8 * 1024**2 + 1))
    with pytest.raises(ContractError) as raised:
        operation(context(tmp_path))
    assert raised.value.code == 'RESOURCE_LIMIT'
