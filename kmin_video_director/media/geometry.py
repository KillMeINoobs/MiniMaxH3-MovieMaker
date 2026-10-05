"""Displayed orientation/SAR, declared pad geometry and its inverse."""
from fractions import Fraction

from ..contracts import SpatialTransform, stable_id
from ..errors import fail
from .timing import fraction, rational, half_up

SPATIAL_VERSION = 'kvd-display-pad/1.0.0'


def display_size(media):
    v = media['probe']['video']
    if v is None:
        fail('UNSUPPORTED_CAPABILITY', 'A selected video stream is required.')
    angle = v['rotation'] % 360
    if angle not in (0, 90, 180, 270) or fraction(v['sar']) <= 0:
        fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'M1 supports positive SAR and orthogonal display rotation.')
    matrix = v['display_matrix']
    if matrix:
        unit = 65536
        if (len(matrix) != 9 or any(matrix[i] for i in (2, 5, 6, 7)) or matrix[8] != 1073741824
            or any(matrix[i] not in (-unit, 0, unit) for i in (0, 1, 3, 4))
            or matrix[0] * matrix[4] - matrix[1] * matrix[3] != unit * unit
            or matrix[0]**2 + matrix[1]**2 != unit * unit):
            fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'Scaled, reflected or translated display matrices need a separate policy.')
    w = max(1, half_up(v['width'] * fraction(v['sar'])))
    h = v['height']
    return (h, w) if angle in (90, 270) else (w, h)


def spatial_transform(media, *, grid=32):
    if grid != 32:
        fail('UNSUPPORTED_CAPABILITY', 'The checked shared M1 profile requires grid 32.')
    v = media['probe']['video']
    w, h = display_size(media)
    cw, ch = ((w + grid - 1) // grid * grid, (h + grid - 1) // grid * grid)
    return SpatialTransform.from_dict({'id': stable_id('space', SPATIAL_VERSION, v),
        'version': SPATIAL_VERSION, 'coded_width': v['width'], 'coded_height': v['height'],
        'source_sar': v['sar'], 'display_matrix': v['display_matrix'], 'display_width': w,
        'display_height': h, 'scale': rational(Fraction(1)), 'fitted_width': w, 'fitted_height': h,
        'canvas_width': cw, 'canvas_height': ch,
        'content_rect': {'x': (cw - w) // 2, 'y': (ch - h) // 2, 'width': w, 'height': h},
        'pad_fill': {'rgb': [0, 0, 0], 'control': [0, 0, 0], 'mask': 0},
        'resampler': 'ffmpeg-bilinear', 'color_conversion': 'rgb24', 'output_width': w,
        'output_height': h, 'output_sar': rational(Fraction(1))})


def display_filter(media):
    v = media['probe']['video']
    display_size(media)  # Validate before constructing the trusted numeric filter.
    w = max(1, half_up(v['width'] * fraction(v['sar'])))
    filters = [f'scale={w}:{v["height"]}:flags=bilinear', 'setsar=1']
    angle = v['rotation'] % 360
    if angle == 90:
        filters.append('transpose=cclock')
    elif angle == 270:
        filters.append('transpose=clock')
    elif angle == 180:
        filters.extend(('hflip', 'vflip'))
    return ','.join(filters)


def inverse_filter(spatial):
    r = spatial['content_rect']
    return f'crop={r["width"]}:{r["height"]}:{r["x"]}:{r["y"]}:exact=1,setsar=1'
