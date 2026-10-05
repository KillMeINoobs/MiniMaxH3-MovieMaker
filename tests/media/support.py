"""Only tiny constructed frame-number/color/impulse media; never user fixtures."""
import os
from pathlib import Path
import subprocess
import wave
from array import array
from functools import lru_cache
import pytest

from kmin_video_director.contracts.worker import OperationContext, CancellationFlag


@lru_cache
def backend_path(name):
    value = os.environ.get('KVD_TEST_' + name.upper(), '')
    if not value:
        pytest.skip('Explicit reviewed synthetic-test backend not selected: KVD_TEST_' + name.upper())
    path = Path(value)
    if not path.is_absolute() or not path.is_file():
        pytest.fail('The explicitly selected synthetic-test backend is not an existing absolute executable.')
    return str(path)


def context(root, **values):
    return OperationContext(root, CancellationFlag(), {'ffmpeg_path': backend_path('ffmpeg'),
        'ffprobe_path': backend_path('ffprobe'), 'disk_quota_bytes': '67108864',
        'working_set_bytes': '16777216', **{k: str(v) for k, v in values.items()}})


def command(args, data=None):
    p = subprocess.run(args, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=0x08000000 if os.name == 'nt' else 0)
    assert p.returncode == 0, p.stderr.decode('utf-8', 'replace')[-1800:]
    return p.stdout


def numbered_frame(index, width=37, height=19):
    # RGB encodes the absolute frame number, with a visible binary number strip.
    pixel = bytes((index % 256, index // 256 % 256, 73))
    data = bytearray(pixel * width * height)
    for bit in range(min(12, width)):
        if index & (1 << bit):
            for y in range(min(3, height)):
                at = (y * width + bit) * 3
                data[at:at+3] = b'\xff\xff\xff'
    return bytes(data)


def video(root, *, count=6, rate='24', width=37, height=19, pts=None, name='Сцена 1.nut', origin=0, sar=None):
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    filters = []
    if pts is not None:
        expression = str(pts[-1])
        for i in reversed(range(len(pts) - 1)):
            expression = f'if(eq(N,{i}),{pts[i]},{expression})'
        filters += ['settb=1/120', 'setpts=' + expression.replace(',', '\\,')]
    elif origin:
        filters += [f'setpts=PTS+{origin}']
    if sar:
        filters += [f'setsar={sar}']
    args = [backend_path('ffmpeg'), '-v', 'error', '-nostdin', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
            '-s', f'{width}x{height}', '-framerate', rate, '-i', 'pipe:0']
    if filters:
        args += ['-vf', ','.join(filters)]
    args += ['-an', '-c:v', 'ffv1', '-pix_fmt', 'bgr0', '-threads', '1', '-fps_mode', 'passthrough',
             '-enc_time_base', '1:120' if pts is not None else '0', '-f', 'nut', str(target)]
    command(args, b''.join(numbered_frame(i, width, height) for i in range(count)))
    return target


def raw_video(path, *, stream=None):
    return command([backend_path('ffmpeg'), '-v', 'error', '-nostdin', '-i', str(path),
                    '-map', '0:v:0' if stream is None else f'0:{stream}',
                    '-an', '-pix_fmt', 'rgb24', '-fps_mode', 'passthrough', '-f', 'rawvideo', 'pipe:1'])


def multistream_video(root, *, count=6, width=37, height=19, leading_audio=False):
    """Two tiny equal-timing video tracks with different independently known pixels."""
    tracks = []
    for slot, base in enumerate((1000, 2000)):
        path = root / f'track-{slot}.nut'
        command([backend_path('ffmpeg'), '-v', 'error', '-nostdin', '-f', 'rawvideo',
            '-pix_fmt', 'rgb24', '-s', f'{width}x{height}', '-framerate', '24', '-i', 'pipe:0',
            '-an', '-c:v', 'ffv1', '-pix_fmt', 'bgr0', '-threads', '1', '-enc_time_base', '1:24',
            '-f', 'nut', str(path)], b''.join(numbered_frame(base + i, width, height) for i in range(count)))
        tracks.append(path)
    if leading_audio:
        tracks[0] = with_audio(root, tracks[0], samples=count * 2000)
    output = root / 'two video tracks.nut'
    args = [backend_path('ffmpeg'), '-v', 'error', '-nostdin', '-i', str(tracks[0]), '-i', str(tracks[1])]
    if leading_audio:
        args += ['-map', '0:a:0']
    command(args + ['-map', '0:v:0', '-map', '1:v:0', '-c', 'copy', '-f', 'nut', str(output)])
    return output


def with_audio(root, clip, *, samples=24000, rate=48000, impulses=(0, 4000, 8000), offset='0'):
    wav = root / 'impulses.wav'
    data = array('h', [0]) * samples
    for i in impulses:
        if 0 <= i < samples:
            data[i] = 24000
    with wave.open(str(wav), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(data.tobytes())
    target = root / 'sound.nut'
    command([backend_path('ffmpeg'), '-v', 'error', '-nostdin', '-copyts', '-i', str(clip),
        '-itsoffset', offset, '-i', str(wav), '-map', '0:v:0', '-map', '1:a:0',
        '-c:v', 'copy', '-c:a', 'pcm_s16le', '-f', 'nut', str(target)])
    return target
