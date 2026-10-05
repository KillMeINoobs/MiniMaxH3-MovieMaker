"""Bounded adapter RGB I/O using the reviewed media backend and decoded PTS.

Native tensors stay runtime-only. The media owner remains authoritative for
backend budgets/cancellation, stream selection, fingerprints and CFR receipts.
"""
import subprocess

from ...contracts import canonical_bytes
from ...contracts.worker import ProjectLocator, StreamSelection
from ...errors import fail
from ...media.backend import (backend, bounded_operation, Budget, check_media, limit,
                             process, target, with_role, write_json as media_write_json)
from ...media.normalize import encoder_args, read_frame
from ...media.probe import probe_media, verify_cfr

VERSION = 'kvd-h3-rgb-io/2.0.0'
integer_limit = limit


def reserve(context, expected):
    budget = Budget(context)
    budget.reserve(expected)
    return budget.quota


def decode_rgb(media, n, width, height, *, context):
    if any(type(v) is not int or v <= 0 for v in (n, width, height)) or n > 345:
        fail('RESOURCE_LIMIT', 'RGB decode requires one bounded positive window.')
    size = width * height * 3
    if size * 3 > limit(context, 'working_set_bytes', 268435456):
        fail('RESOURCE_LIMIT', 'RGB decode exceeds the explicit frame-buffer budget.')
    path = check_media(media, context)
    video = media['probe']['video']
    if video is None or (video['width'], video['height']) != (width, height):
        fail('FRAME_COUNT_MISMATCH', 'RGB decode geometry differs from its checked media.')
    verify_cfr(media, n, context)
    ffmpeg, _, _ = backend(context)
    budget = Budget(context)
    args = [ffmpeg, '-v', 'error', '-nostdin', '-noautorotate', '-i', str(path),
            '-map', f'0:{media["fingerprint"]["video_stream"]}', '-an', '-sn', '-dn',
            '-threads', '1', '-fps_mode', 'passthrough', '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1']
    with process(args, context, budget) as decoder:
        for _ in range(n):
            context.cancellation.check()
            yield bytes(read_frame(decoder.stdout, size))
        if decoder.stdout.read(1):
            fail('FRAME_COUNT_MISMATCH', 'Decoded RGB contains undeclared frames or geometry.')


@bounded_operation
def encode_rgb(frames, relative, n, width, height, *, context, output_width=None, output_height=None):
    out_width = output_width or width
    out_height = output_height or height
    if any(type(v) is not int or v <= 0 for v in (n, width, height, out_width, out_height)) or n > 345:
        fail('FRAME_COUNT_MISMATCH', 'Useful RGB output must be one exact bounded window.')
    if max(width * height, out_width * out_height) * 9 > limit(context, 'working_set_bytes', 268435456):
        fail('RESOURCE_LIMIT', 'Useful RGB output exceeds its selected frame-buffer budget.')
    ffmpeg, _, _ = backend(context)
    budget = Budget(context)
    budget.reserve(n * (out_width * out_height * 4 + 256))
    locator = {'scheme': 'project_relative', 'path': relative}
    with target(locator, context, budget) as temporary:
        args = encoder_args(ffmpeg, width, height, temporary)
        if (out_width, out_height) != (width, height):
            args[-1:-1] = ['-vf', f'scale={out_width}:{out_height}:flags=lanczos,setsar=1']
        count = 0
        with process(args, context, budget, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL) as encoder:
            for frame in frames:
                context.cancellation.check()
                if count >= n or len(frame) != width * height * 3:
                    fail('FRAME_COUNT_MISMATCH', 'Useful encoder received incorrect RGB geometry/count.')
                encoder.stdin.write(frame)
                count += 1
                budget.check()
            if count != n:
                fail('FRAME_COUNT_MISMATCH', 'Useful encoder received an incomplete window.')
    # Same streamed PTS rows, EOF and stream fingerprints as media preparation/export.
    found = probe_media(ProjectLocator(relative), StreamSelection(), context=context)
    verify_cfr(found.media, n, context)
    video = found.media['probe']['video']
    if (video['width'], video['height']) != (out_width, out_height):
        fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'Decoded useful output differs from its inverse transform.')
    return with_role(found.media, 'render_video')


def write_json(value, relative, context):
    budget = Budget(context)
    budget.reserve(len(canonical_bytes(value)))
    media_write_json({'scheme': 'project_relative', 'path': relative}, value, context, budget)
