"""One whole-source displayed-hold resample to CFR24 video and global PCM."""
from fractions import Fraction
import subprocess
import wave

from ..contracts import MediaRef, AudioTimeline, cache_key, cache_locator, canonical_bytes
from ..contracts.confined_io import selected_path
from ..contracts.worker import JsonObject, OperationContext, NormalizedOutput, ProjectLocator, StreamSelection
from ..errors import fail
from .backend import backend, Budget, check_media, limit, process, target, write_json, read_json, media_ref, with_role, bounded_operation
from .geometry import display_size, display_filter
from .probe import probe_media, frame_rows, verify_cfr, probe_receipt_locator
from .timing import TIMING_VERSION, fraction, rational, quantize, sample_boundary

DEFAULT_RECIPE = {'version': 'kvd-normalize/1.0.0', 'resampler': 'displayed_hold',
    'fps': {'num': 24, 'den': 1}, 'geometry': 'preserve_display', 'sample_rate': 48000,
    'audio_mode': 'preserve', 'gap_policy': 'hold', 'video_codec': 'ffv1-nut'}


def validate_recipe(recipe):
    if (set(recipe) != set(DEFAULT_RECIPE) or any(recipe[k] != DEFAULT_RECIPE[k] for k in
        ('version', 'resampler', 'fps', 'geometry', 'gap_policy', 'video_codec'))
        or recipe['audio_mode'] not in ('preserve', 'mute') or type(recipe['sample_rate']) is not int
        or not 8000 <= recipe['sample_rate'] <= 192000):
        fail('UNSUPPORTED_CAPABILITY', 'Select the documented versioned CFR24 recipe and preserve/mute audio policy.')


def read_frame(pipe, size):
    frame = bytearray()
    while len(frame) < size:
        block = pipe.read(size - len(frame))
        if not block:
            break
        frame.extend(block)
    if len(frame) != size:
        fail('FRAME_COUNT_MISMATCH', 'The source decoder did not produce the manifested frame count.')
    return frame


def encoder_args(ffmpeg, w, h, target_path, *, audio_path=None, codec='ffv1-nut', pad_even=False):
    args = [ffmpeg, '-v', 'error', '-nostdin', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{w}x{h}', '-framerate', '24', '-i', 'pipe:0']
    if audio_path:
        args += ['-i', str(audio_path)]
    args += ['-map', '0:v:0', '-threads', '1']
    if codec == 'ffv1-nut':
        args += ['-c:v', 'ffv1', '-pix_fmt', 'bgr0', '-enc_time_base', '1:24']
        if audio_path:
            args += ['-map', '1:a:0', '-c:a', 'pcm_s16le']
        args += ['-f', 'nut']
    elif codec == 'h264-aac':
        if (w % 2 or h % 2) and not pad_even:
            fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'H.264 yuv420p requires even dimensions. Choose FFV1 or explicit export padding.')
        if pad_even and (w % 2 or h % 2):
            args += ['-vf', f'pad={w+(w%2)}:{h+(h%2)}:0:0:black']
        args += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-video_track_timescale', '24000']
        if audio_path:
            args += ['-map', '1:a:0', '-c:a', 'aac', '-b:a', '192k']
        args += ['-movflags', '+faststart', '-f', 'mp4']
    else:
        fail('UNSUPPORTED_CAPABILITY', 'The requested export codec policy is not implemented.')
    return args + [str(target_path)]


def pcm_manifest(locator, fs, channels, versions, context):
    with wave.open(str(selected_path(context.asset_root, locator['path'])), 'rb') as w:
        if (w.getframerate(), w.getnchannels(), w.getsampwidth()) != (fs, channels, 2):
            fail('AUDIO_SYNC_MISMATCH', 'The global PCM format differs from the selected policy.')
        samples = w.getnframes()
    return media_ref(locator, 'audio_pcm', {'video': None, 'audio': {'codec': 'pcm_s16le', 'stream_index': 0,
        'time_base': rational(Fraction(1, fs)), 'first_pts': 0, 'sample_rate': fs, 'channels': channels,
        'skip_samples': 0}}, versions, context), samples


@bounded_operation
def normalize_media(media: MediaRef, recipe: JsonObject, *, context: OperationContext) -> NormalizedOutput:
    context.cancellation.check()
    validate_recipe(recipe)
    source_path = check_media(media, context)
    if media['role'] != 'source_video':
        fail('UNSUPPORTED_CAPABILITY', 'Normalize the selected original source once, not an already prepared window.')
    ffmpeg, ffprobe, versions = backend(context)
    v, a = media['probe']['video'], media['probe']['audio']
    source_timing = read_json(probe_receipt_locator(media), context)
    tb = fraction(v['time_base'])
    norm = quantize((v['end_pts'] - v['first_pts']) * tb)
    norm.update(version=DEFAULT_RECIPE['version'], t0=rational(v['first_pts'] * tb))
    width, height = display_size(media)
    pixels = width * height * 3
    if pixels * 3 > limit(context, 'working_set_bytes', 256 * 1024**2):
        fail('RESOURCE_LIMIT', 'The active frame buffers exceed the declared working-set budget.')
    key = cache_key('temporal', {'source': media['fingerprint']['digest'], 'streams': [v['stream_index'], a['stream_index'] if a else None],
        'pts': v['pts_digest'], 'end_pts': v['end_pts'], 'backend': versions, 'recipe': dict(recipe),
        'display': [width, height, v['rotation'], v['sar']]}, algorithm_version=TIMING_VERSION)
    meta = cache_locator('temporal', key)
    if selected_path(context.asset_root, meta['path']).is_file():
        hit = read_json(meta, context)
        if hit['normalization']['report'].get('source_digest') != media['fingerprint']['digest']:
            fail('STALE_DEPENDENCY', 'The normalization receipt belongs to different source content.')
        canonical = MediaRef.from_dict(hit['media'])
        check_media(canonical, context)
        # All dependent disk manifests must close, even on a cache hit.
        from .backend import hash_file
        selection = selected_path(context.asset_root, hit['normalization']['report']['selection_manifest']['path'])
        if hash_file(selection, context) != hit['normalization']['report']['selection_digest']:
            fail('SOURCE_CHANGED', 'The canonical selection manifest changed.')
        if hit['normalization']['report'].get('pcm_media'):
            check_media(MediaRef.from_dict(hit['normalization']['report']['pcm_media']), context)
        verify_cfr(canonical, norm['frame_count'], context)
        return NormalizedOutput(canonical, hit['normalization'], AudioTimeline.from_dict(hit['audio_timeline']))
    budget = Budget(context)
    samples = sample_boundary(norm['frame_count'], recipe['sample_rate'])
    budget.reserve(norm['frame_count'] * (pixels + 256) + (samples * (a['channels'] if a else 1) * 2))
    out_locator = cache_locator('temporal', key, suffix='nut')
    selections = cache_locator('temporal', key, suffix='jsonl')
    rows = iter(frame_rows(media, context))
    current = next(rows, None)
    if current is None:
        fail('AMBIGUOUS_MEDIA_TIMING', 'The decoded timestamp index is empty.')
    dropped, duplicates, gap_count, written, source_count = 0, 0, 0, 0, 0
    reports = []
    with target(out_locator, context, budget) as tmp_video, target(selections, context, budget) as tmp_select:
        with tmp_select.open('wb') as selection_file:
            decoder = [ffmpeg, '-v', 'error', '-nostdin', '-noautorotate', '-i', str(source_path), '-map', f'0:{v["stream_index"]}',
                '-an', '-vf', display_filter(media), '-pix_fmt', 'rgb24', '-threads', '1', '-fps_mode', 'passthrough', '-f', 'rawvideo', 'pipe:1']
            with process(decoder, context, budget) as decode, process(encoder_args(ffmpeg, width, height, tmp_video), context, budget, stdin=subprocess.PIPE) as encode:
                while current is not None:
                    context.cancellation.check()
                    following = next(rows, None)
                    frame = read_frame(decode.stdout, pixels)
                    next_time = ((following['pts'] - v['first_pts']) * tb if following else None)
                    used = 0
                    gap_count += bool(following and current['duration'] > 0 and following['pts'] > current['pts'] + current['duration'])
                    while written < norm['frame_count'] and (next_time is None or Fraction(written, 24) < next_time):
                        encode.stdin.write(frame)
                        selection_file.write(canonical_bytes({'frame': written, 'source_frame': current['frame'],
                            'source_pts': current['pts'], 'time': rational(Fraction(written, 24))}) + b'\n')
                        written += 1
                        used += 1
                        budget.check()
                    dropped += used == 0
                    duplicates += max(0, used - 1)
                    source_count += 1
                    current = following
                if decode.stdout.read(1):
                    fail('FRAME_COUNT_MISMATCH', 'The source decoder produced extra unmanifested frames.')
            reports += [decode.kvd_report, encode.kvd_report]
    from .backend import hash_file
    found = probe_media(ProjectLocator(out_locator['path']), StreamSelection(), context=context)
    canonical = with_role(found.media, 'prepared_video')
    verified = verify_cfr(canonical, norm['frame_count'], context)
    offset = (fraction(a['time_base']) * a['first_pts'] - fraction(norm['t0'])) if a else Fraction(0)
    pcm = None
    if a and recipe['audio_mode'] == 'preserve':
        pcm_locator = cache_locator('temporal', key, suffix='wav')
        fs, channels = recipe['sample_rate'], a['channels']
        if channels not in (1, 2):
            fail('UNSUPPORTED_CAPABILITY', 'M1 global PCM supports explicit mono/stereo sources.')
        origin = fraction(norm['t0'])
        af = f'asetpts=PTS-({origin.numerator}/{origin.denominator})/TB,aresample={fs}:async=1:first_pts=0:min_hard_comp=0,apad,atrim=end_sample={samples}'
        with target(pcm_locator, context, budget) as temporary:
            args = [ffmpeg, '-v', 'error', '-nostdin', '-y', '-copyts', '-i', str(source_path), '-map', f'0:{a["stream_index"]}',
                '-vn', '-af', af, '-ar', str(fs), '-ac', str(channels), '-c:a', 'pcm_s16le', '-threads', '1', '-f', 'wav', str(temporary)]
            with process(args, context, budget, stdout=subprocess.DEVNULL) as audio_process:
                pass
        reports.append(audio_process.kvd_report)
        pcm, actual_samples = pcm_manifest(pcm_locator, fs, channels, versions, context)
        if actual_samples != samples:
            fail('AUDIO_SYNC_MISMATCH', 'The global PCM does not reach the exact absolute sample endpoint.')
    audio = AudioTimeline.from_dict({'mode': recipe['audio_mode'], 'source_media_id': media.id if a else None,
        'source_offset': rational(offset), 'sample_rate': recipe['sample_rate'],
        'channel_layout': 'stereo' if a and a['channels'] == 2 else 'mono', 'decisions': [],
        'rounding': 'absolute_half_up', 'sample_count': samples, 'codec': {'pcm': 's16le'},
        'presentation': {'version': 'kvd-global-pcm/1.0.0', 'origin': norm['t0'], 'decoder_applies_skip_samples': True}})
    norm['pts_digest'] = verified['pts_digest']
    norm['report'] = {'recipe': dict(recipe), 'backend': versions, 'source_digest': media['fingerprint']['digest'],
        'source_pts_digest': v['pts_digest'],
        'endpoint_policy': source_timing['endpoint_policy'], 'final_frame_duration': source_timing['final_frame_duration'],
        'source_decoded_frames': source_count, 'source_origin': norm['t0'], 'source_end_pts': v['end_pts'],
        'dropped_frames': dropped, 'duplicated_frames': duplicates, 'timestamp_gap_holds': gap_count,
        'last_frame_hold_seconds': rational(max(Fraction(0), fraction(norm['duration_error']))),
        'selection_manifest': selections, 'selection_digest': hash_file(selected_path(context.asset_root, selections['path']), context),
        'pcm_media': pcm.to_dict() if pcm else None, 'display_dimensions': [width, height],
        'active_pixel_buffer_bound_bytes': pixels * 3, 'processes': reports,
        'operation_disk_peak_bytes': budget.peak_bytes, 'gpu': 'not_performed'}
    check_media(media, context)
    write_json(meta, {'media': canonical.to_dict(), 'normalization': norm, 'audio_timeline': audio.to_dict()}, context, budget)
    return NormalizedOutput(canonical, norm, audio)
