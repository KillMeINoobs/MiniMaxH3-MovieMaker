"""Constructed CPU window outputs, never inference or personal media."""

from kmin_video_director.contracts import RenderResult, Project, RenderProfile, SpatialTransform, canonical_bytes, resolve_project
from kmin_video_director.contracts.worker import ProjectLocator, StreamSelection
from tests.contracts.example_data import profile
from tests.media.support import context, video, command, numbered_frame, with_audio


def prepared_project(root, frames=24, *, width=37, height=19, sound=False, sample_rate=48000, impulses=None):
    from kmin_video_director.media.probe import probe_media
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    from kmin_video_director.media.project import create_project, apply_plan
    from kmin_video_director.planning.windows import plan_windows
    ctx = context(root)
    source = video(root, count=frames, width=width, height=height)
    if sound:
        source = with_audio(root, source, samples=(frames * sample_rate + 12)//24, rate=sample_rate,
                            impulses=impulses or (0, sample_rate//24, (frames * sample_rate + 12)//24-1))
    found = probe_media(ProjectLocator(source.name), StreamSelection(audio=1 if sound else None), context=ctx)
    normalized = normalize_media(found.media, {**DEFAULT_RECIPE, 'sample_rate': sample_rate}, context=ctx)
    p = create_project(found.media, normalized, RenderProfile.from_dict(profile()))
    plan = plan_windows(resolve_project(p), RenderProfile.from_dict(profile()), context=ctx)
    return apply_plan(p, plan), ctx


def cpu_results(project, ctx):
    from kmin_video_director.media.probe import probe_media, verify_cfr
    from kmin_video_director.media.backend import with_role
    from kmin_video_director.media.geometry import inverse_filter
    results = []
    pd = project.to_dict()
    for wd in pd['windows'].values():
        s = SpatialTransform.from_dict(pd['spatial_transforms'][wd['spatial_transform_id']])
        u = wd['useful_range']['end'] - wd['useful_range']['start']
        native = ctx.asset_root / f'native-{wd["ordinal"]}.nut'
        artifact = ctx.asset_root / f'render-{wd["ordinal"]}.nut'
        cw, ch, rect = s['canvas_width'], s['canvas_height'], s['content_rect']
        raw = bytearray()
        for j in range(wd['inference_frame_count']):
            content = numbered_frame(wd['useful_range']['start'] + min(j, u - 1) + 1000,
                                     s['output_width'], s['output_height'])
            frame = bytearray(cw * ch * 3)
            for y in range(rect['height']):
                at = ((y + rect['y']) * cw + rect['x']) * 3
                frame[at:at+rect['width']*3] = content[y*rect['width']*3:(y+1)*rect['width']*3]
            raw.extend(frame)
        command([ctx.versions['ffmpeg_path'], '-v', 'error', '-nostdin', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
            '-s', f'{cw}x{ch}', '-framerate', '24', '-i', 'pipe:0', '-c:v', 'ffv1', '-pix_fmt', 'bgr0',
            '-threads', '1', '-enc_time_base', '1:24', '-f', 'nut', str(native)], bytes(raw))
        measured = probe_media(ProjectLocator(native.name), StreamSelection(), context=ctx)
        native_check = verify_cfr(measured.media, wd['inference_frame_count'], ctx)
        command([ctx.versions['ffmpeg_path'], '-v', 'error', '-nostdin', '-i', str(native),
            '-vf', f'trim=end_frame={u},' + inverse_filter(s), '-c:v', 'ffv1', '-pix_fmt', 'bgr0',
            '-threads', '1', '-enc_time_base', '1:24', '-fps_mode', 'passthrough', '-f', 'nut', str(artifact)])
        found = probe_media(ProjectLocator(artifact.name), StreamSelection(), context=ctx)
        media = with_role(found.media, 'render_video')
        verify_cfr(media, u, ctx)
        receipt = f'cpu-window-{wd["ordinal"]}.json'
        (ctx.asset_root / receipt).write_bytes(canonical_bytes({'evidence': 'synthetic_cpu', 'gpu': 'not_performed',
            'native': native_check, 'useful': u, 'spatial_crop': s['content_rect']}))
        result = RenderResult.from_dict({'kind': 'kmin.render_result', 'schema_version': '2.0.0',
            'id': f'cpu-result-{wd["ordinal"]}', 'request_id': f'cpu-request-{wd["ordinal"]}', 'attempt': 1,
            'project_id': project.id, 'segment_id': wd['segment_id'], 'window_id': wd['id'],
            'generation_key': wd['generation_key'], 'status': 'succeeded', 'stage': 'trim',
            'progress': {'done': 1, 'total': 1, 'unit': 'window'}, 'artifacts': [media.to_dict()],
            'coverage': {'useful_range': wd['useful_range'], 'output_useful_range': wd['output_useful_range'],
                'requested_frames': wd['inference_frame_count'], 'decoded_frames': native_check['decoded_frames'],
                'useful_frames': u, 'width': s['output_width'], 'height': s['output_height'],
                'fps': {'num': 24, 'den': 1}, 'padding_removed': True, 'context_removed': True,
                'pts_digest': found.media['probe']['video']['pts_digest']},
            'audio': None, 'provenance': {'evidence': 'constructed_cpu_numbers', 'spatial_transform_id': s.id},
            'validation': {'evidence_kind': 'cpu_media', 'gpu': 'not_performed', 'receipts': [receipt]},
            'error': None, 'warnings': ['Synthetic CPU media; no H3 inference.']})
        pd['results'][result.id] = result.to_dict()
        pd['active_result_by_window'][wd['id']] = result.id
        results.append(result)
    return Project.from_dict(pd), tuple(results)
