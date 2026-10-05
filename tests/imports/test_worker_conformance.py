"""Validate the documented call boundary without invoking downstream work."""
import inspect
from typing import get_origin, get_type_hints, get_args, Union
from types import UnionType

import pytest

from kmin_video_director.contracts import ContractError, canonical_bytes
from kmin_video_director.contracts.worker import OPERATION_TYPES
from kmin_video_director.registration import build_registry
from tests.contracts.worker_examples import operation_inputs


def matches(value, annotation):
    origin = get_origin(annotation)
    if origin in (Union, UnionType):
        return any(matches(value, a) for a in get_args(annotation))
    if origin is not None:
        return isinstance(value, origin)
    return isinstance(value, annotation)


@pytest.mark.parametrize("name", sorted(OPERATION_TYPES))
def test_typed_operation_call_examples(name, tmp_path):
    values = operation_inputs(tmp_path)[name]
    protocol = OPERATION_TYPES[name]
    inspect.signature(protocol.__call__).bind(None, **values)
    hints = get_type_hints(protocol.__call__)
    assert all(matches(value, hints[key]) for key, value in values.items())
    assert not list(tmp_path.iterdir())  # Call-shape construction performs no I/O.
    with pytest.raises(ContractError, match="UNSUPPORTED_CAPABILITY"):
        build_registry().require_operation(name)


def test_runtime_links_and_values_are_not_portable_json(tmp_path):
    examples = operation_inputs(tmp_path)
    with pytest.raises(ContractError, match="INVALID_JSON"):
        canonical_bytes(examples["FinalizeWindow"]["decoded"])
    assert examples["AssembleExport"]["results"][0]["status"] == "planned"
    assert examples["ExpandNativeRender"]["models"].model.as_list() == ["synthetic-model", 0]
