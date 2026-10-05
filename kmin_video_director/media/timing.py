"""Exact rational timing and absolute audio boundaries."""
from fractions import Fraction

from ..errors import fail

TIMING_VERSION = 'kvd-displayed-hold/1.0.0'


def rational(value):
    value = Fraction(value)
    return {'num': value.numerator, 'den': value.denominator}


def fraction(value):
    return Fraction(value['num'], value['den'])


def half_up(value):
    value = Fraction(value)
    return (value.numerator * 2 + value.denominator) // (value.denominator * 2)


def quantize(duration):
    duration = Fraction(duration)
    if duration <= 0:
        fail('AMBIGUOUS_MEDIA_TIMING', 'A positive decoded presentation span is required.')
    rounded = half_up(duration * 24)
    frames = max(1, rounded)
    return {'duration': rational(duration), 'rounded_frame_count': rounded, 'frame_count': frames,
        'duration_error': rational(Fraction(frames, 24) - duration),
        'duration_clamp': {'applied': rounded == 0, 'reason': 'minimum_one_frame' if rounded == 0 else None,
            'before_frame_count': rounded, 'after_frame_count': frames}}


def sample_boundary(frame, sample_rate):
    if type(frame) is not int or frame < 0 or type(sample_rate) is not int or sample_rate <= 0:
        fail('INVALID_RECORD', 'Audio boundaries require nonnegative frames and a positive sample rate.')
    return (frame * sample_rate + 12) // 24
