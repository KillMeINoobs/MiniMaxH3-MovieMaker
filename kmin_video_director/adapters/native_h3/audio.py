"""Native H3 decoded stereo PCM -> exact useful global-Q samples, never inference."""
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import subprocess
import wave

from ...contracts import resolve_locator
from ...errors import ContractError, fail
from ...media.backend import Budget, limit, process, target
from ...media.normalize import pcm_manifest
from ...media.timing import half_up, sample_boundary

VERSION = 'kvd-h3-generated-pcm/1.0.0'
NATIVE_RATE = 32000
NATIVE_CHANNELS = 2


def native_sample_count(frames):
    # Pinned temporal_shape uses 40 latent ticks/s; the native VAE hop is800.
    return round(Fraction(frames * 40, 24)) * 800


@dataclass(frozen=True)
class NativePCM:
    audio: object
    count: int
    digest: dict
    synthetic: bool

    def chunks(self, context):
        if self.synthetic:
            data = self.audio['pcm_s16le']
            for at in range(0, len(data), 4096 * NATIVE_CHANNELS * 2):
                context.cancellation.check()
                yield data[at:at + 4096 * NATIVE_CHANNELS * 2]
        else:
            import torch
            waveform = self.audio['waveform']
            for at in range(0, self.count, 4096):
                context.cancellation.check()
                block = waveform[0, :, at:at + 4096]
                if not bool(torch.isfinite(block).all()) or bool((block.abs() > 1).any()):
                    fail('AUDIO_SYNC_MISMATCH', 'Native AUDIO must contain finite stereo values in -1..1.')
                block = block.detach().to(device='cpu', dtype=torch.float32).transpose(0, 1)
                yield block.mul(32767).round().to(torch.int16).contiguous().numpy().astype('<i2', copy=False).tobytes()


def prepare_native_pcm(audio, frames, *, synthetic, context):
    if not isinstance(audio, dict) or type(audio.get('sample_rate')) is not int or audio['sample_rate'] != NATIVE_RATE:
        fail('AUDIO_SYNC_MISMATCH', 'Generate requires the checked native H3 32000Hz stereo AUDIO.')
    count = native_sample_count(frames)
    if synthetic:
        if (type(audio.get('channels')) is not int or audio['channels'] != NATIVE_CHANNELS
            or not isinstance(audio.get('pcm_s16le'), bytes) or len(audio['pcm_s16le']) != count * NATIVE_CHANNELS * 2):
            fail('AUDIO_SYNC_MISMATCH', 'Identified synthetic stereo PCM must match the exact native audio grid.')
    else:
        try:
            import torch
        except ImportError:
            fail('DEPENDENCY_MISSING', 'Native AUDIO finalization requires the existing Torch backend.')
        waveform = audio.get('waveform')
        if (not isinstance(waveform, torch.Tensor) or not waveform.is_floating_point()
            or tuple(waveform.shape) != (1, NATIVE_CHANNELS, count)):
            fail('AUDIO_SYNC_MISMATCH', 'Native AUDIO must have exact batch1/stereo/sample-count geometry.')
    if count * NATIVE_CHANNELS * 4 + 4096 * NATIVE_CHANNELS * 8 > limit(context, 'working_set_bytes', 268435456):
        fail('RESOURCE_LIMIT', 'The bounded decoded AUDIO exceeds its declared working-set budget.')
    pcm = NativePCM(audio, count, {}, synthetic)
    digest = hashlib.sha256()
    for block in pcm.chunks(context):
        digest.update(block)
    return NativePCM(audio, count, {'algorithm': 'sha256', 'hex': digest.hexdigest()}, synthetic)


def finalize_pcm(pcm, window, timeline, relative, *, ffmpeg, versions, context):
    fs = timeline['sample_rate']
    if timeline['channel_layout'] not in ('mono', 'stereo'):
        fail('AUDIO_SYNC_MISMATCH', 'Generated useful PCM requires explicit mono/stereo output layout.')
    channels = 1 if timeline['channel_layout'] == 'mono' else 2
    useful = window['output_useful_range']
    global_range = window['useful_range']
    begin = sample_boundary(useful['start'], NATIVE_RATE)
    end = sample_boundary(useful['end'], NATIVE_RATE)
    local_count = end - begin
    expected = sample_boundary(global_range['end'], fs) - sample_boundary(global_range['start'], fs)
    budget = Budget(context)
    budget.reserve((half_up(Fraction(local_count * fs, NATIVE_RATE)) + expected) * channels * 2 + 8192)
    locator = {'scheme': 'project_relative', 'path': relative}
    # Resample once, then fit its measured output at the end. There is no
    # per-window phase offset or change to the original global source origin.
    resampled = {'scheme': 'project_relative', 'path': relative + '.resampled.wav'}
    resampled_path = resolve_locator(context.asset_root, resampled['path'])
    try:
        with target(resampled, context, budget) as temporary:
            args = [ffmpeg, '-v', 'error', '-nostdin', '-y', '-f', 's16le', '-ar', str(NATIVE_RATE),
                '-ac', str(NATIVE_CHANNELS), '-i', 'pipe:0', '-af', f'aresample={fs}', '-ar', str(fs), '-ac', str(channels),
                '-threads', '1', '-c:a', 'pcm_s16le', '-f', 'wav', str(temporary)]
            with process(args, context, budget, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL) as encoder:
                cursor = written = 0
                for block in pcm.chunks(context):
                    samples = len(block) // (NATIVE_CHANNELS * 2)
                    low, high = max(begin, cursor), min(end, cursor + samples)
                    if high > low:
                        encoder.stdin.write(block[(low - cursor) * NATIVE_CHANNELS * 2:
                                                  (high - cursor) * NATIVE_CHANNELS * 2])
                        written += high - low
                    cursor += samples
                    budget.check()
                    if cursor >= end:
                        break
                # Quantized native audio can end a fraction of one latent tick
                # before its video. Fit that declared local endpoint once.
                if written < local_count:
                    encoder.stdin.write(b'\0' * (local_count - written) * NATIVE_CHANNELS * 2)
        with wave.open(str(resampled_path), 'rb') as src:
            if (src.getframerate(), src.getnchannels(), src.getsampwidth()) != (fs, channels, 2):
                fail('AUDIO_SYNC_MISMATCH', 'The useful PCM resampler changed the requested format.')
            measured = src.getnframes()
            tolerance = (fs + NATIVE_RATE - 1) // NATIVE_RATE + 2
            if abs(expected - measured) > tolerance:
                fail('AUDIO_SYNC_MISMATCH', 'Generated PCM differs beyond the declared rounding fit.')
            with target(locator, context, budget) as temporary:
                with wave.open(str(temporary), 'wb') as dst:
                    dst.setframerate(fs); dst.setnchannels(channels); dst.setsampwidth(2)
                    remaining = min(expected, measured)
                    while remaining:
                        context.cancellation.check()
                        block = src.readframes(min(4096, remaining))
                        got = len(block) // (channels * 2)
                        if not got:
                            fail('AUDIO_SYNC_MISMATCH', 'Useful PCM ended before its measured boundary.')
                        dst.writeframesraw(block)
                        remaining -= got
                        budget.check()
                    if expected > measured:
                        dst.writeframesraw(b'\0' * (expected - measured) * channels * 2)
        media, count = pcm_manifest(locator, fs, channels, versions, context)
        if count != expected:
            fail('AUDIO_SYNC_MISMATCH', 'Durable useful PCM differs from the absolute global Q interval.')
        report = {'version': VERSION, 'mode': 'generate', 'policy': 'absolute_global_q_useful_pcm',
            'sample_rate': fs, 'channels': channels, 'native_sample_rate': NATIVE_RATE,
            'native_channels': NATIVE_CHANNELS, 'native_sample_count': pcm.count, 'native_pcm_digest': pcm.digest,
            'native_quantization_correction': pcm.count - sample_boundary(window['inference_frame_count'], NATIVE_RATE),
            'local_useful_sample_range': {'start': begin, 'end': end},
            'global_useful_sample_range': {'start': sample_boundary(global_range['start'], fs),
                                          'end': sample_boundary(global_range['end'], fs)},
            'native_useful_pad_samples': max(0, end - max(begin, min(end, pcm.count))),
            'native_discarded_before_samples': min(begin, pcm.count), 'native_discarded_after_samples': max(0, pcm.count - end),
            'resampled_samples': measured, 'expected_samples': expected, 'measured_samples': count,
            'sample_phase_fit': expected - measured,
            'absolute_q_phase_fit': expected - sample_boundary(global_range['end'] - global_range['start'], fs),
            'source_offset': timeline['source_offset'], 'native_audio_retained': True,
            'pcm_quantization': 's16le_round_32767' if not pcm.synthetic else 'identified_synthetic_s16le',
            'resample_count': 1, 'process': encoder.kvd_report}
        return media, report
    except (OSError, wave.Error):
        raise ContractError('AUDIO_SYNC_MISMATCH', 'The bounded useful PCM could not be finalized.') from None
    finally:
        try:
            resampled_path.unlink(missing_ok=True)
        except OSError:
            pass  # It is not an active artifact or receipt.
