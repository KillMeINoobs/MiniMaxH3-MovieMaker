import pytest

from kmin_video_director.contracts.worker import ProjectLocator, StreamSelection
from tests.media.support import context, video


def test_normalization_reuse_and_source_project_binding(tmp_path):
    from kmin_video_director.media.probe import probe_media
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    from kmin_video_director.media.project import create_project, source_profile
    ctx = context(tmp_path); src = video(tmp_path)
    found = probe_media(ProjectLocator(src.name), StreamSelection(), context=ctx)
    normalized = normalize_media(found.media, DEFAULT_RECIPE, context=ctx)
    hit = normalize_media(found.media, DEFAULT_RECIPE, context=ctx)
    assert hit == normalized
    other = video(tmp_path, name='other.nut')
    other.write_bytes(other.read_bytes() + b'different-content')
    other_probe = probe_media(ProjectLocator(other.name), StreamSelection(), context=ctx)
    with pytest.raises(ValueError, match='STALE_DEPENDENCY'):
        create_project(other_probe.media, normalized, source_profile())
    manifest = tmp_path / normalized.normalization['report']['selection_manifest']['path']
    manifest.write_bytes(manifest.read_bytes() + b'changed')
    with pytest.raises(ValueError, match='SOURCE_CHANGED'):
        normalize_media(found.media, DEFAULT_RECIPE, context=ctx)
