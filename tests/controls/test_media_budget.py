"""Owned raw-map/receipt I/O consumes the reviewed aggregate media budget.

The bytes are constructed RGB fixtures, not native Canny contour evidence.
"""
import pytest

from kmin_video_director.contracts.worker import CancellationFlag, OperationContext
from kmin_video_director.errors import ContractError
from kmin_video_director.media.backend import bounded_operation
from kmin_video_director.controls.storage import write_raw
from kmin_video_director.adapters.native_h3.media_bridge import write_json


def test_raw_map_and_recipe_share_one_operation_disk_budget(tmp_path):
    count, width, height = 124, 32, 32
    raw_size = count * width * height * 3
    context = OperationContext(tmp_path, CancellationFlag(), {'disk_quota_bytes': str(raw_size + 1024)})

    @bounded_operation
    def requested(*, context):
        write_raw((bytes(width * height * 3) for _ in range(count)), 'map.rgb',
                  count, width, height, 'control_map', 'identified_rgb_fixture', context)
        write_json({'fixture_receipt': 'x' * 4096}, 'map.json', context)

    with pytest.raises(ContractError, match='RESOURCE_LIMIT'):
        requested(context=context)
    assert (tmp_path / 'map.rgb').stat().st_size == raw_size
    assert not (tmp_path / 'map.json').exists()
    assert not list(tmp_path.rglob('*.partial'))
