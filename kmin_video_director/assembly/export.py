"""Streaming exact useful-video assembly and one final soundtrack encode."""
from typing import Sequence
import subprocess
import wave

from ..contracts import Project, RenderResult, AudioTimeline, MediaRef, cache_key, cache_locator, stable_id, digest_json
from ..contracts.worker import JsonObject, OperationContext, ExportOutput, ProjectLocator, StreamSelection
from ..contracts.confined_io import selected_path
from ..errors import fail
from ..media.backend import backend, check_media, Budget, process, target, write_json, with_role, limit, bounded_operation, regular
from ..media.normalize import encoder_args, read_frame
from ..media.probe import probe_media, verify_cfr
from ..media.timing import sample_boundary

EXPORT_VERSION = 'kvd-assembly/1.0.0'
DEFAULT_POLICY = {'version': 'kvd-export/1.0.0', 'codec': 'ffv1-nut',
                  'selection': 'full', 'odd_dimensions': 'reject'}


def selected_windows(project, selection):
    scenes = [s for s in project['segments'] if selection == 'full' or s['selected']]
    if not scenes:
        fail('PARTIAL_RESULT', 'Select at least one scene for export.', stage='export')
    windows = []
    for scene in scenes:
        owned = sorted((w for w in project['windows'].values() if w['segment_id'] == scene['id']),
                       key=lambda w: w['useful_range']['start'])
        cursor = scene['useful_range']['start']
        for w in owned:
            if w['useful_range']['start'] != cursor:
                fail('PARTIAL_RESULT', 'The selected scene has a useful coverage gap or overlap.', stage='export',
                     details={'segment_id': scene['id'], 'missing_from_frame': cursor})
            cursor = w['useful_range']['end']
        if cursor != scene['useful_range']['end']:
            fail('PARTIAL_RESULT', 'The selected scene has no complete window plan.', stage='export',
                 details={'segment_id': scene['id'], 'missing_from_frame': cursor})
        windows.extend(owned)
    return windows


def validate_outputs(project, results, windows, context):
    incoming = {r.id: r for r in results}
    if len(incoming) != len(results):
        fail('DUPLICATE_ID', 'Each selected result must be supplied once.', stage='export')
    active = {project['active_result_by_window'].get(w['id']) for w in windows}
    if set(incoming) - active:
        fail('STALE_DEPENDENCY', 'Supplied results include records outside the explicit export selection.', stage='export')
    selected = []
    for w in windows:
        rid = project['active_result_by_window'].get(w['id'])
        if rid is None or rid not in incoming:
            fail('PARTIAL_RESULT', 'A selected window has no supplied active successful result.', stage='export',
                 details={'window_id': w['id'], 'useful_range': w['useful_range']})
        r = incoming[rid]
        if r.to_dict() != project['results'].get(rid) or r['generation_key'] != w['generation_key']:
            fail('STALE_DEPENDENCY', 'The supplied result differs from the explicitly selected current record.', stage='export')
        if r['status'] != 'succeeded' or r['project_id'] != project.id or r['window_id'] != w['id']:
            fail('PARTIAL_RESULT', 'Only successful matching render results may be assembled.', stage='export')
        for receipt in r['validation']['receipts']:
            regular(selected_path(context.asset_root, ProjectLocator(receipt).path))
        artifacts = [a for a in r['artifacts'] if a['role'] == 'render_video']
        if len(artifacts) != 1:
            fail('PARTIAL_RESULT', 'Each selected result must identify one useful render-video artifact.', stage='export')
        media = MediaRef.from_dict(artifacts[0])
        check_media(media, context)
        u = w['useful_range']['end'] - w['useful_range']['start']
        actual = probe_media(ProjectLocator(media['locator']['path']),
            StreamSelection(video=media['fingerprint']['video_stream']), context=context).media
        if actual['probe']['video'] != media['probe']['video']:
            fail('STALE_DEPENDENCY', 'Actual decoded render timing/geometry differs from its supplied probe.', stage='export')
        verified = verify_cfr(actual, u, context)
        s = project['spatial_transforms'][w['spatial_transform_id']]
        v = media['probe']['video']
        if (v['width'], v['height']) != (s['output_width'], s['output_height']) or v['rotation'] or v['sar'] != {'num': 1, 'den': 1}:
            fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'A useful render artifact must already have the exact inverse-cropped output geometry.', stage='export')
        if verified['pts_digest'] != r['coverage']['pts_digest']:
            fail('STALE_DEPENDENCY', 'The useful output PTS digest differs from the selected result.', stage='export')
        selected.append((w, r, media))
    if set(incoming) != {r.id for _, r, _ in selected}:
        fail('STALE_DEPENDENCY', 'Supplied results include records outside the explicit export selection.', stage='export')
    return selected


def _wave_check(path, fs, channels):
    try:
        f = wave.open(str(path), 'rb')
        if (f.getframerate(), f.getnchannels(), f.getsampwidth()) != (fs, channels, 2):
            f.close()
            fail('AUDIO_SYNC_MISMATCH', 'Audio PCM must match the explicit sample rate, layout and s16 format.', stage='export')
        return f
    except (OSError, wave.Error):
        fail('AUDIO_SYNC_MISMATCH', 'The selected PCM artifact cannot be decoded.', stage='export')


def _write_slice(src, dst, start, count, channels, context):
    src.setpos(start)
    left = count
    while left:
        context.cancellation.check()
        block = src.readframes(min(4096, left))
        frames = len(block) // (channels * 2)
        if not frames:
            fail('AUDIO_SYNC_MISMATCH', 'PCM ended before its exact global boundary.', stage='export')
        dst.writeframesraw(block)
        left -= frames


def splice_audio(project, selected, audio, locator, ffmpeg, versions, context, budget):
    fs = audio['sample_rate']
    layout = audio['channel_layout']
    if layout not in ('mono', 'stereo') or audio['sample_count'] != sample_boundary(project['frame_count'], fs):
        fail('AUDIO_SYNC_MISMATCH', 'Audio must use the exact project-wide sample endpoint and mono/stereo layout.')
    channels = 1 if layout == 'mono' else 2
    decisions = {d['segment_id']: d['mode'] for d in audio['decisions']}
    if len(decisions) != len(audio['decisions']) or set(decisions) - {s['id'] for s in project['segments']}:
        fail('AUDIO_SYNC_MISMATCH', 'Audio scene decisions must identify unique existing scenes.')
    modes = [decisions.get(w['segment_id'], audio['mode']) for w, _, _ in selected]
    global_ref = project['normalization']['report'].get('pcm_media')
    source_has_audio = project['media'][project['source_media_id']]['probe']['audio'] is not None
    if all(m == 'mute' for m in modes) or all(m == 'preserve' for m in modes) and global_ref is None and not source_has_audio:
        return None, {'stream': False, 'global_pcm_samples': 0, 'decoded_samples': 0,
                      'final_encode_count': 0, 'note': 'muted' if all(m == 'mute' for m in modes) else 'no_source_audio'}
    if any(m == 'preserve' for m in modes) and global_ref is None:
        fail('AUDIO_SYNC_MISMATCH', 'A mixed preserve soundtrack requires its global PCM artifact.')
    global_path = check_media(MediaRef.from_dict(global_ref), context) if global_ref else None
    if global_path:
        if audio['source_media_id'] != project['source_media_id'] or audio['source_offset'] != project['audio_timeline']['source_offset']:
            fail('STALE_DEPENDENCY', 'Source PCM must retain its original source binding and origin.')
        with wave.open(str(global_path), 'rb') as src:
            old_rate, old_channels, old_frames = src.getframerate(), src.getnchannels(), src.getnframes()
        if old_channels != channels or old_frames != sample_boundary(project['frame_count'], old_rate):
            fail('AUDIO_SYNC_MISMATCH', 'Global PCM sample count/layout is stale.')
        if old_rate != fs:
            resampled = {'scheme': 'project_relative', 'path': locator['path'] + '.global.wav'}
            with target(resampled, context, budget) as tmp:
                args = [ffmpeg, '-v', 'error', '-nostdin', '-y', '-i', str(global_path), '-af',
                    f'aresample={fs},apad,atrim=end_sample={audio["sample_count"]}', '-ar', str(fs), '-c:a', 'pcm_s16le', '-f', 'wav', str(tmp)]
                with process(args, context, budget, stdout=subprocess.DEVNULL):
                    pass
            global_path = selected_path(context.asset_root, resampled['path'])
    # Group contiguous equal-mode ranges before slicing PCM. Technical windows
    # never create a new rounding origin. A selection discontinuity may require
    # one final sample at the end of its entire contiguous run.
    runs = []
    for item, mode in zip(selected, modes):
        if (runs and runs[-1][1] == mode
            and runs[-1][0][-1][0]['useful_range']['end'] == item[0]['useful_range']['start']):
            runs[-1][0].append(item)
        else:
            runs.append(([item], mode))
    cumulative_frames = 0
    corrections = []
    with target(locator, context, budget) as temporary:
        with wave.open(str(temporary), 'wb') as dst:
            dst.setnchannels(channels); dst.setsampwidth(2); dst.setframerate(fs)
            for items, mode in runs:
                a = items[0][0]['useful_range']['start']
                b = items[-1][0]['useful_range']['end']
                u = b - a
                count = sample_boundary(b, fs) - sample_boundary(a, fs)
                # Full contiguous export is exactly global Q. Selected-only output
                # has its own origin; account for its at-most-one-sample phase fit.
                needed = sample_boundary(cumulative_frames + u, fs) - sample_boundary(cumulative_frames, fs)
                if mode == 'mute':
                    left = needed
                    while left:
                        context.cancellation.check()
                        chunk = min(left, 4096)
                        dst.writeframesraw(b'\0' * chunk * channels * 2)
                        left -= chunk
                else:
                    if mode == 'preserve':
                        with _wave_check(global_path, fs, channels) as src:
                            _write_slice(src, dst, sample_boundary(a, fs), min(count, needed), channels, context)
                    else:
                        remaining = min(count, needed)
                        for window, result, _ in items:
                            artifacts = [m for m in result['artifacts'] if m['role'] == 'audio_pcm']
                            if len(artifacts) != 1:
                                fail('AUDIO_SYNC_MISMATCH', 'Generate mode requires an explicitly useful-trimmed PCM artifact per result.')
                            input_path = check_media(MediaRef.from_dict(artifacts[0]), context)
                            bounds = window['useful_range']
                            native_count = sample_boundary(bounds['end'], fs) - sample_boundary(bounds['start'], fs)
                            with _wave_check(input_path, fs, channels) as src:
                                if src.getnframes() != native_count:
                                    fail('AUDIO_SYNC_MISMATCH', 'Generated useful PCM must already fit its absolute window interval.')
                                amount = min(remaining, native_count)
                                _write_slice(src, dst, 0, amount, channels, context)
                                remaining -= amount
                    if needed > count:
                        dst.writeframesraw(b'\0' * (needed - count) * channels * 2)
                    if count != needed:
                        corrections.append({'useful_range': {'start': a, 'end': b}, 'sample_phase_fit': needed - count})
                cumulative_frames += u
                budget.check()
    total = sample_boundary(cumulative_frames, fs)
    with _wave_check(selected_path(context.asset_root, locator['path']), fs, channels) as src:
        if src.getnframes() != total:
            fail('AUDIO_SYNC_MISMATCH', 'Assembled global PCM is not the exact output sample count.')
    return selected_path(context.asset_root, locator['path']), {'stream': True, 'global_pcm_samples': total,
        'sample_rate': fs, 'channels': channels, 'source_offset': audio['source_offset'],
        'sample_phase_corrections': corrections, 'final_encode_count': 1}


def audio_receipt(path, ffmpeg, ffprobe, stream, fs, channels, expected, context, budget):
    decoded_bytes = 0
    with process([ffmpeg, '-v', 'error', '-nostdin', '-i', str(path), '-map', f'0:{stream}',
                  '-vn', '-f', 's16le', '-acodec', 'pcm_s16le', 'pipe:1'], context, budget) as p:
        while True:
            block = p.stdout.read(65536)
            if not block:
                break
            decoded_bytes += len(block)
    samples = decoded_bytes // (channels * 2)
    if decoded_bytes % (channels * 2) or abs(samples - expected) > sample_boundary(1, fs):
        fail('AUDIO_SYNC_MISMATCH', 'Decoded soundtrack duration exceeds one frame of the exact global PCM.')
    skip, discard = 0, 0
    with process([ffprobe, '-v', 'error', '-select_streams', str(stream), '-show_packets', '-show_entries',
        'packet_side_data=skip_samples,discard_padding', '-of', 'compact=p=0', str(path)], context, budget) as p:
        for line in p.stdout:
            for field in line.decode().strip().split('|'):
                if '=' in field:
                    key, value = field.split('=', 1)
                    key = key.rsplit(':', 1)[-1]  # FFprobe8 qualified side_datum keys.
                    if key == 'skip_samples':
                        skip += int(value)
                    elif key == 'discard_padding':
                        discard += int(value)
    return {'decoded_samples': samples, 'codec_skip_samples': skip, 'codec_discard_padding': discard,
        'decoded_trailing_samples': samples - expected, 'decoder_applies_signaled_priming': True}


@bounded_operation
def assemble_export(project: Project, results: Sequence[RenderResult], audio: AudioTimeline, export_policy: JsonObject,
                    *, context: OperationContext) -> ExportOutput:
    context.cancellation.check()
    if (set(export_policy) != set(DEFAULT_POLICY) or export_policy['version'] != DEFAULT_POLICY['version']
        or export_policy['codec'] not in ('ffv1-nut', 'h264-aac') or export_policy['selection'] not in ('full', 'selected')
        or export_policy['odd_dimensions'] not in ('reject', 'pad_even')):
        fail('UNSUPPORTED_CAPABILITY', 'Select the documented versioned export policy.')
    windows = selected_windows(project, export_policy['selection'])
    selected = validate_outputs(project, results, windows, context)
    dimensions = {(m['probe']['video']['width'], m['probe']['video']['height']) for _, _, m in selected}
    if len(dimensions) != 1:
        fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'All selected outputs must share the same display geometry.')
    w, h = next(iter(dimensions))
    codec = export_policy['codec']
    pad_even = export_policy['odd_dimensions'] == 'pad_even'
    if codec == 'h264-aac' and (w % 2 or h % 2) and not pad_even:
        fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'H.264 needs even dimensions; choose FFV1 or explicit codec padding.')
    ew, eh = (w + w % 2, h + h % 2) if codec == 'h264-aac' and pad_even else (w, h)
    pixels = w * h * 3
    if pixels * 3 > limit(context, 'working_set_bytes', 256 * 1024**2):
        fail('RESOURCE_LIMIT', 'Active assembly frame buffers exceed the declared budget.')
    ffmpeg, ffprobe, versions = backend(context)
    total = sum(b['useful_range']['end'] - b['useful_range']['start'] for b in windows)
    key = cache_key('assembly', {'chosen': [{'id': r.id, 'generation_key': r['generation_key'],
        'coverage': r['coverage'], 'artifacts': [a['fingerprint']['digest'] for a in r['artifacts']]} for _, r, _ in selected],
        'audio': audio.to_dict(), 'source_pcm_digest': project['normalization']['report'].get('pcm_media', {})['fingerprint']['digest']
            if project['normalization']['report'].get('pcm_media') else None,
        'policy': dict(export_policy), 'backend': versions}, algorithm_version=EXPORT_VERSION)
    locator = cache_locator('assembly', key, suffix='nut' if codec == 'ffv1-nut' else 'mp4')
    receipt = cache_locator('assembly', key)
    pcm_locator = cache_locator('assembly', key, suffix='wav')
    budget = Budget(context)
    budget.reserve(total * (pixels + 256) + sample_boundary(total, audio['sample_rate']) * 4)
    soundtrack, sound_report = splice_audio(project, selected, audio, pcm_locator, ffmpeg, versions, context, budget)
    processes = []
    with target(locator, context, budget) as temporary:
        with process(encoder_args(ffmpeg, w, h, temporary, audio_path=soundtrack, codec=codec, pad_even=pad_even),
                     context, budget, stdin=subprocess.PIPE) as encode:
            for window, result, media in selected:
                path = check_media(media, context)
                u = window['useful_range']['end'] - window['useful_range']['start']
                args = [ffmpeg, '-v', 'error', '-nostdin', '-i', str(path), '-map', '0:v:0', '-an',
                    '-pix_fmt', 'rgb24', '-threads', '1', '-fps_mode', 'passthrough', '-f', 'rawvideo', 'pipe:1']
                with process(args, context, budget) as decode:
                    for j in range(u):
                        context.cancellation.check()
                        encode.stdin.write(read_frame(decode.stdout, pixels))
                        budget.check()
                    if decode.stdout.read(1):
                        fail('FRAME_COUNT_MISMATCH', 'A useful render artifact contains extra frames.')
                processes.append(decode.kvd_report)
        processes.append(encode.kvd_report)
    found = probe_media(ProjectLocator(locator['path']), StreamSelection(audio=1 if soundtrack else None), context=context)
    output = with_role(found.media, 'render_video')
    video_report = verify_cfr(output, total, context)
    v = output['probe']['video']
    if (v['width'], v['height']) != (ew, eh):
        fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'Actual export dimensions differ from the declared codec policy.')
    if soundtrack:
        decoded_audio = output['probe']['audio']
        if decoded_audio['sample_rate'] != audio['sample_rate'] or decoded_audio['channels'] != sound_report['channels']:
            fail('AUDIO_SYNC_MISMATCH', 'Actual encoded soundtrack format differs from the requested PCM.')
        sound_report.update(audio_receipt(selected_path(context.asset_root, locator['path']), ffmpeg, ffprobe,
            output['probe']['audio']['stream_index'], audio['sample_rate'], sound_report['channels'],
            sound_report['global_pcm_samples'], context, budget))
        if codec == 'ffv1-nut' and sound_report['decoded_samples'] != sound_report['global_pcm_samples']:
            fail('AUDIO_SYNC_MISMATCH', 'Lossless PCM export must have the exact sample count.')
    for _, _, m in selected:
        check_media(m, context)
    if project['normalization']['report'].get('pcm_media') and soundtrack:
        check_media(MediaRef.from_dict(project['normalization']['report']['pcm_media']), context)
    for _, result, _ in selected:
        for artifact in result['artifacts']:
            if artifact['role'] == 'audio_pcm':
                check_media(MediaRef.from_dict(artifact), context)
    report = {'version': EXPORT_VERSION, 'backend': versions, 'video': video_report, 'audio': sound_report,
        'global_ranges': [w['useful_range'] for w, _, _ in selected], 'selected_result_ids': [r.id for _, r, _ in selected],
        'export_dimensions': [ew, eh], 'source_display_dimensions': [w, h], 'policy': dict(export_policy),
        'processes': processes, 'active_pixel_buffer_bound_bytes': pixels * 3,
        'operation_disk_peak_bytes': budget.peak_bytes, 'gpu': 'not_performed'}
    write_json(receipt, report, context, budget)
    result = RenderResult.from_dict({'kind': 'kmin.render_result', 'schema_version': '2.0.0',
        'id': stable_id('export', key), 'request_id': stable_id('export_request', key), 'attempt': 1,
        'project_id': project.id, 'segment_id': None, 'window_id': None, 'generation_key': key,
        'status': 'succeeded', 'stage': 'export', 'progress': {'done': total, 'total': total, 'unit': 'frame'},
        'artifacts': [output.to_dict()], 'coverage': {'useful_range': {'start': 0, 'end': total},
            'output_useful_range': {'start': 0, 'end': total}, 'requested_frames': total, 'decoded_frames': total,
            'useful_frames': total, 'width': ew, 'height': eh, 'fps': {'num': 24, 'den': 1},
            'padding_removed': True, 'context_removed': True, 'pts_digest': video_report['pts_digest']},
        'audio': sound_report, 'provenance': {'version': EXPORT_VERSION, 'selected_result_ids': report['selected_result_ids'],
            'global_ranges': report['global_ranges'], 'receipt_digest': digest_json(report)},
        'validation': {'evidence_kind': 'cpu_media', 'gpu': 'not_performed', 'receipts': [receipt['path']]},
        'error': None, 'warnings': ['CPU assembly/export does not establish H3 or live ComfyUI acceptance.']})
    return ExportOutput(result, report)
