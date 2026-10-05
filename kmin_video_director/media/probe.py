"""Actual decoded presentation timestamps with explicit displayed origin and EOF."""
from fractions import Fraction
import hashlib
import json
import re

from ..contracts import cache_key, cache_locator, canonical_bytes
from ..contracts.confined_io import selected_path
from ..contracts.worker import ProjectLocator, StreamSelection, OperationContext, ProbeOutput
from ..errors import fail
from .backend import backend, capture, regular, hash_file, Budget, process, target, write_json, media_ref, bounded_operation
from .timing import rational, fraction

PROBE_VERSION = 'kvd-decoded-pts/1.0.0'


def index_locator(media):
    return cache_locator('temporal', media['probe']['video']['pts_digest'], suffix='jsonl')


def probe_receipt_locator(media):
    key = cache_key('temporal', {'source': media['fingerprint']['digest'], 'probe': media['probe'],
        'probe_version': media['fingerprint']['probe_version'], 'decoder_version': media['fingerprint']['decoder_version']},
        algorithm_version=PROBE_VERSION)
    return cache_locator('temporal', key)


def frame_rows(media, context):
    locator = index_locator(media)
    path = regular(selected_path(context.asset_root, locator['path']))
    if hash_file(path, context) != media['probe']['video']['pts_digest']:
        fail('SOURCE_CHANGED', 'The decoded timestamp manifest changed.')
    with path.open(encoding='utf-8') as f:
        for line in f:
            context.cancellation.check()
            yield json.loads(line)


def _frame_lines(ffprobe, path, stream, context, budget):
    args = [ffprobe, '-v', 'error', '-select_streams', str(stream), '-show_frames', '-show_entries',
            'frame=best_effort_timestamp,pts,duration,pkt_duration,width,height,nb_samples:frame_side_data=skip_samples',
            '-of', 'compact=p=0:nk=0', str(path)]
    with process(args, context, budget) as p:
        while True:
            line = p.stdout.readline(65537)
            if not line:
                break
            if len(line) > 65536:
                fail('RESOURCE_LIMIT', 'Decoded frame metadata exceeds its bounded line limit.')
            fields = {key.rsplit(':', 1)[-1]: value for key, value in
                (part.split('=', 1) for part in line.decode('utf-8', 'replace').strip().split('|') if '=' in part)}
            if 'best_effort_timestamp' in fields or 'pts' in fields:
                yield fields


def _pts(row):
    value = row.get('best_effort_timestamp', row.get('pts'))
    try:
        return int(value)
    except (ValueError, TypeError):
        fail('AMBIGUOUS_MEDIA_TIMING', 'A displayed decoded frame has no usable timestamp.')


@bounded_operation
def probe_media(locator: ProjectLocator, selection: StreamSelection, *, context: OperationContext) -> ProbeOutput:
    context.cancellation.check()
    path = regular(selected_path(context.asset_root, locator.path))
    source_digest = hash_file(path, context)
    ffmpeg, ffprobe, versions = backend(context)
    raw = json.loads(capture([ffprobe, '-v', 'error', '-show_streams', '-of', 'json', str(path)], context))
    streams = {s['index']: s for s in raw['streams']}
    v = streams.get(selection.video)
    a = streams.get(selection.audio) if selection.audio is not None else None
    if v is None or v.get('codec_type') != 'video' or selection.audio is not None and (a is None or a.get('codec_type') != 'audio'):
        fail('AMBIGUOUS_MEDIA_TIMING', 'Select existing absolute video/audio stream indices explicitly.')
    tb = Fraction(v['time_base'])
    if tb <= 0:
        fail('AMBIGUOUS_MEDIA_TIMING', 'The video time base must be positive.')
    budget = Budget(context)
    key = cache_key('temporal', {'source': source_digest, 'video': selection.video, 'audio': selection.audio,
        'backend': versions, 'endpoint_duration': context.versions.get('endpoint_duration', '')}, algorithm_version=PROBE_VERSION)
    staging = cache_locator('temporal', key, suffix='jsonl')
    count, first, previous, interval = 0, None, None, None
    vfr = False
    gaps = 0
    pts_hash = hashlib.sha256()
    with target(staging, context, budget) as temporary:
        with temporary.open('wb') as f:
            for row in _frame_lines(ffprobe, path, selection.video, context, budget):
                pts = _pts(row)
                if previous is not None:
                    delta = pts - previous['pts']
                    if delta <= 0:
                        fail('AMBIGUOUS_MEDIA_TIMING', 'Displayed timestamps must increase strictly; duplicate/backward PTS are ambiguous.')
                    interval = interval or delta
                    vfr |= delta != interval
                    gaps += bool(previous['duration'] and delta > previous['duration'])
                if int(row.get('width', v['width'])) != v['width'] or int(row.get('height', v['height'])) != v['height']:
                    fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'Changing coded dimensions require a separate media policy.')
                duration = row.get('duration', row.get('pkt_duration', '0'))
                previous = {'frame': count, 'pts': pts, 'duration': int(duration) if duration not in ('N/A', '') else 0}
                first = pts if first is None else first
                data = canonical_bytes(previous) + b'\n'
                pts_hash.update(data)
                f.write(data)
                count += 1
                if count % 256 == 0:
                    budget.check()
        if previous is None:
            fail('AMBIGUOUS_MEDIA_TIMING', 'The selected stream has no displayed frames.')
        final_duration = previous['duration']
        endpoint_policy = 'decoded_last_frame_duration'
        if final_duration <= 0:
            explicit = context.versions.get('endpoint_duration')
            if not explicit:
                fail('AMBIGUOUS_MEDIA_TIMING', 'Decoded EOF lacks a final-frame duration. Supply an explicit duration in seconds.')
            try:
                ticks = Fraction(explicit) / tb
            except (ValueError, ZeroDivisionError):
                fail('AMBIGUOUS_MEDIA_TIMING', 'The explicit final-frame duration is invalid.')
            if ticks <= 0 or ticks.denominator != 1:
                fail('AMBIGUOUS_MEDIA_TIMING', 'The explicit final duration must be positive and exact on the source time base.')
            final_duration = ticks.numerator
            endpoint_policy = 'explicit_final_frame_duration'
    digest = {'algorithm': 'sha256', 'hex': pts_hash.hexdigest()}
    index = cache_locator('temporal', digest, suffix='jsonl')
    # Publish a content-addressed PTS index without buffering the film's timestamps.
    with target(index, context, budget) as temporary:
        import shutil
        with selected_path(context.asset_root, staging['path']).open('rb') as src, temporary.open('wb') as dst:
            shutil.copyfileobj(src, dst, length=65536)
    selected_path(context.asset_root, staging['path']).unlink(missing_ok=True)
    rotation, matrix = 0, []
    for side in v.get('side_data_list', []):
        rotation = side.get('rotation', rotation)
        if side.get('displaymatrix'):
            matrix = [int(n) for line in side['displaymatrix'].strip().splitlines()
                      for n in re.findall(r'-?\d+', line.partition(':')[2])]
    try:
        sar = Fraction(v.get('sample_aspect_ratio', '1:1').replace(':', '/'))
    except (ValueError, ZeroDivisionError):
        fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'The selected source has no unambiguous sample aspect ratio.')
    if sar <= 0:
        fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'The selected source needs a positive sample aspect ratio.')
    # Tiny NUT streams legitimately report average_rate=0/0. Actual frame
    # spacing (or an explicitly decoded single-frame duration) is independent
    # evidence; nominal-rate metadata never determines the presentation span.
    measured_step = interval or (final_duration if count == 1 else None)
    rate = 1 / (measured_step * tb) if measured_step and not vfr else Fraction(0)
    video = {'codec': v['codec_name'], 'stream_index': selection.video, 'time_base': rational(tb),
        'first_pts': first, 'end_pts': previous['pts'] + final_duration, 'pts_digest': digest,
        'rate': rational(rate), 'vfr': vfr, 'width': v['width'], 'height': v['height'],
        'rotation': rotation, 'sar': rational(sar), 'display_matrix': matrix,
        'color': v.get('color_space', 'unspecified'), 'pixel_format': v.get('pix_fmt', 'unknown')}
    audio = None
    if a is not None:
        first_audio, skip = None, 0
        for row in _frame_lines(ffprobe, path, selection.audio, context, budget):
            if first_audio is None:
                first_audio = _pts(row)
                skip = int(row.get('skip_samples', 0))
        if first_audio is None:
            fail('AMBIGUOUS_MEDIA_TIMING', 'The selected audio stream has no effective decoded frames.')
        audio = {'codec': a['codec_name'], 'stream_index': selection.audio, 'time_base': rational(Fraction(a['time_base'])),
            'first_pts': first_audio, 'sample_rate': int(a['sample_rate']), 'channels': a['channels'], 'skip_samples': skip}
    m = media_ref({'scheme': locator.scheme, 'path': locator.path}, 'source_video', {'video': video, 'audio': audio}, versions, context)
    if m['fingerprint']['digest'] != source_digest:
        fail('SOURCE_CHANGED', 'The source changed while its displayed timestamps were probed.')
    timing = {'version': PROBE_VERSION, 'backend': versions, 'decoded_frames': count,
        't0': rational(first * tb), 'duration': rational((video['end_pts'] - first) * tb),
        'endpoint_policy': endpoint_policy, 'final_frame_duration': rational(final_duration * tb),
        'pts_manifest': index, 'timestamp_gaps': gaps}
    write_json(probe_receipt_locator(m), timing, context, budget)
    return ProbeOutput(m, timing)


def verify_cfr(media, count, context):
    v = media['probe']['video']
    tb = fraction(v['time_base'])
    observed = 0
    for row in frame_rows(media, context):
        if row['pts'] * tb != Fraction(observed, 24):
            fail('FRAME_COUNT_MISMATCH', 'The actual decoded output is not PTS j/24.')
        observed += 1
    if observed != count or v['end_pts'] * tb != Fraction(count, 24):
        fail('FRAME_COUNT_MISMATCH', 'Decoded CFR frame count or EOF duration differs from the requested output.')
    return {'decoded_frames': observed, 'fps': {'num': 24, 'den': 1}, 'pts_digest': v['pts_digest']}
