import pytest

from kmin_video_director.contracts.worker import ProjectLocator, StreamSelection
from tests.media.support import context, video, multistream_video, raw_video, numbered_frame


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


@pytest.mark.parametrize('normalized_stream,other_stream', [(0, 1), (1, 0)])
def test_project_rejects_same_file_cross_video_selection(tmp_path, normalized_stream, other_stream):
    from kmin_video_director.media.probe import probe_media
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    from kmin_video_director.media.project import create_project, source_profile
    ctx = context(tmp_path)
    source = multistream_video(tmp_path)
    chosen = probe_media(ProjectLocator(source.name), StreamSelection(video=normalized_stream), context=ctx).media
    other = probe_media(ProjectLocator(source.name), StreamSelection(video=other_stream), context=ctx).media
    assert chosen['fingerprint']['digest'] == other['fingerprint']['digest']
    assert chosen['probe']['video']['pts_digest'] == other['probe']['video']['pts_digest']
    assert chosen.id != other.id
    normalized = normalize_media(chosen, DEFAULT_RECIPE, context=ctx)
    assert raw_video(tmp_path / normalized.media['locator']['path']) == b''.join(
        numbered_frame((normalized_stream + 1) * 1000 + i) for i in range(6))
    matched = create_project(chosen, normalized, source_profile())
    assert matched['source_media_id'] == chosen.id
    with pytest.raises(ValueError, match='STALE_DEPENDENCY'):
        create_project(other, normalized, source_profile())


def test_project_identity_distinguishes_same_file_video_selections(tmp_path):
    from kmin_video_director.media.probe import probe_media
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    from kmin_video_director.media.project import create_project, source_profile
    ctx = context(tmp_path)
    source = multistream_video(tmp_path)
    projects = []
    for stream in (0, 1):
        chosen = probe_media(ProjectLocator(source.name), StreamSelection(video=stream), context=ctx).media
        normalized = normalize_media(chosen, DEFAULT_RECIPE, context=ctx)
        projects.append(create_project(chosen, normalized, source_profile()))
    assert projects[0]['canonical_media_id'] != projects[1]['canonical_media_id']
    assert projects[0].id != projects[1].id
