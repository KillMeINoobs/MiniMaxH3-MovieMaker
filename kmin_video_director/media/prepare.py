"""One exact bounded disk window, with declared repeat-tail and service padding."""
import subprocess

from ..contracts import MediaRef, GenerationWindow, SpatialTransform, cache_key, cache_locator, require_runtime_capabilities
from ..contracts.confined_io import selected_path
from ..contracts.worker import OperationContext, PreparedArtifact, ProjectLocator, StreamSelection
from ..errors import fail
from .backend import backend, Budget, check_media, limit, process, target, write_json, read_json, with_role, bounded_operation
from .probe import probe_media, verify_cfr
from .timing import fraction

PREPARE_VERSION = 'kvd-disk-window/1.0.0'


@bounded_operation
def prepare_window(window: GenerationWindow, canonical_media: MediaRef, spatial: SpatialTransform,
                   *, context: OperationContext) -> PreparedArtifact:
    context.cancellation.check()
    require_runtime_capabilities(window=window, settings=window['resolved_settings'])
    source = check_media(canonical_media, context)
    v = canonical_media['probe']['video']
    spans = [s for s in window['input_spans'] if s['role'] == 'useful']
    if (canonical_media['role'] != 'prepared_video' or len(spans) != 1
        or spans[0]['media_id'] != canonical_media.id or spatial.id != window['spatial_transform_id']
        or window['output_useful_range']['start'] != 0 or window['padding']['before'] != 0):
        fail('STALE_DEPENDENCY', 'The window must identify this canonical media and exact M1 spatial transform.')
    if (v['width'], v['height']) != (spatial['display_width'], spatial['display_height']):
        fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'Canonical display dimensions differ from the declared transform.')
    if (spatial['fitted_width'], spatial['fitted_height']) != (v['width'], v['height']) or spatial['scale'] != {'num': 1, 'den': 1}:
        fail('UNSUPPORTED_CAPABILITY', 'This M1 preparation implements the explicit preserve-display policy.')
    total = fraction(v['time_base']) * (v['end_pts'] - v['first_pts']) * 24
    if total.denominator != 1:
        fail('FRAME_COUNT_MISMATCH', 'Canonical video duration must lie on CFR24.')
    verify_cfr(canonical_media, total.numerator, context)
    r = spans[0]['source_range']
    if r['end'] > total or r != window['useful_range']:
        fail('COVERAGE_MISMATCH', 'The useful source range is outside the canonical timeline.')
    ffmpeg, ffprobe, versions = backend(context)
    key = cache_key('spatial', {'source': canonical_media['fingerprint']['digest'], 'pts': v['pts_digest'],
        'spans': window['input_spans'], 'spatial': spatial.to_dict(), 'backend': versions}, algorithm_version=PREPARE_VERSION)
    meta, locator = cache_locator('spatial', key), cache_locator('spatial', key, suffix='nut')
    n = window['inference_frame_count']
    cw, ch = spatial['canvas_width'], spatial['canvas_height']
    if cw * ch * 9 > limit(context, 'working_set_bytes', 256 * 1024**2):
        fail('RESOURCE_LIMIT', 'The bounded preparation frame buffers exceed the declared budget.')
    budget = Budget(context)
    budget.reserve(n * (cw * ch * 3 + 256))
    if selected_path(context.asset_root, meta['path']).is_file():
        prepared = MediaRef.from_dict(read_json(meta, context)['media'])
        check_media(prepared, context)
        verify_cfr(prepared, n, context)
        return PreparedArtifact(window.id, prepared, spatial, n)
    rect = spatial['content_rect']
    filters = f'trim=start_frame={r["start"]}:end_frame={r["end"]},setpts=N/(24*TB),pad={cw}:{ch}:{rect["x"]}:{rect["y"]}:black'
    if window['padding']['after']:
        filters += f',tpad=stop_mode=clone:stop={window["padding"]["after"]}'
    filters += ',setsar=1'
    with target(locator, context, budget) as temporary:
        args = [ffmpeg, '-v', 'error', '-nostdin', '-y', '-i', str(source), '-map', f'0:{v["stream_index"]}',
            '-an', '-vf', filters, '-frames:v', str(n), '-threads', '1', '-c:v', 'ffv1', '-pix_fmt', 'bgr0',
            '-fps_mode', 'passthrough', '-enc_time_base', '1:24', '-f', 'nut', str(temporary)]
        with process(args, context, budget, stdout=subprocess.DEVNULL) as p:
            pass
    found = probe_media(ProjectLocator(locator['path']), StreamSelection(), context=context)
    prepared = with_role(found.media, 'prepared_video')
    verify_cfr(prepared, n, context)
    if (prepared['probe']['video']['width'], prepared['probe']['video']['height']) != (cw, ch):
        fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'The actual prepared canvas differs from the exact spatial plan.')
    check_media(canonical_media, context)
    write_json(meta, {'version': PREPARE_VERSION, 'media': prepared.to_dict(), 'frame_count': n,
        'spatial_transform': spatial.to_dict(), 'process': p.kvd_report, 'gpu': 'not_performed'}, context, budget)
    return PreparedArtifact(window.id, prepared, spatial, n)
