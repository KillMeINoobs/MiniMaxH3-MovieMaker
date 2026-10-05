from fractions import Fraction

import pytest

from kmin_video_director.contracts import MediaRef
from tests.contracts.example_data import media


@pytest.mark.parametrize('duration,rounded,count,error', [
    (Fraction(1, 120), 0, 1, Fraction(1, 30)),
    (Fraction(1, 48), 1, 1, Fraction(1, 48)),
    (Fraction(1, 24), 1, 1, Fraction(0)),
    (Fraction(1001, 24000), 1, 1, Fraction(-1, 24000))])
def test_duration_quantization(duration, rounded, count, error):
    from kmin_video_director.media.timing import quantize
    out = quantize(duration)
    assert out['rounded_frame_count'] == rounded and out['frame_count'] == count
    assert Fraction(**{'numerator': out['duration_error']['num'], 'denominator': out['duration_error']['den']}) == error
    assert out['duration_clamp']['applied'] == (rounded == 0)


def test_absolute_samples_do_not_accumulate_per_window_rounding():
    from kmin_video_director.media.timing import sample_boundary
    assert [sample_boundary(f, 32000) for f in range(4)] == [0, 1333, 2667, 4000]
    assert sum(sample_boundary(b, 32000) - sample_boundary(a, 32000)
               for a, b in [(0, 1), (1, 2), (2, 3)]) == 4000


@pytest.mark.parametrize('width,height,sar,rotation,display,canvas', [
    (640, 360, (1, 1), 0, (640, 360), (640, 384)),
    (320, 240, (1, 1), 90, (240, 320), (256, 320)),
    (720, 576, (16, 15), 0, (768, 576), (768, 576)),
    (37, 19, (1, 1), 0, (37, 19), (64, 32)),
    (19, 37, (1, 1), 0, (19, 37), (32, 64))])
def test_declared_display_geometry(width, height, sar, rotation, display, canvas):
    from kmin_video_director.media.geometry import spatial_transform
    m = media()
    m['probe']['video'].update(width=width, height=height, rotation=rotation,
                             sar={'num': sar[0], 'den': sar[1]})
    s = spatial_transform(MediaRef.from_dict(m))
    assert (s['display_width'], s['display_height']) == display
    assert (s['canvas_width'], s['canvas_height']) == canvas
    assert (s['output_width'], s['output_height']) == display
    assert s['content_rect']['width'] == display[0]
