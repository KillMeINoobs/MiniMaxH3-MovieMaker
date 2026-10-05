"""Validate the documented call boundary without invoking downstream work."""
import inspect
import sys
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


@pytest.mark.parametrize("name", sorted(OPERATION_TYPES))
def test_explicitly_empty_registry_rejects_unregistered_operation(name, tmp_path, monkeypatch):
    package_name = "empty_operations_" + name.lower()
    package = tmp_path / package_name
    package.mkdir()
    (package / "__init__.py").write_text("")
    monkeypatch.syspath_prepend(str(tmp_path))
    registry = build_registry(package_name)
    assert not registry.nodes and not registry.operations and not registry.modules
    with pytest.raises(ContractError, match="UNSUPPORTED_CAPABILITY") as error:
        registry.require_operation(name)
    assert error.value.code == "UNSUPPORTED_CAPABILITY"
    assert error.value.details["operation"] == name


def test_call_examples_are_independent_of_registered_handlers(tmp_path, monkeypatch):
    package = tmp_path / "call_shape_extensions"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "guard_nodes.py").write_text(
        "def unexpected_invocation(*args, **kwargs):\n"
        "    raise AssertionError('Conformance must not invoke an operation')\n"
        f"OPERATIONS={{name: unexpected_invocation for name in {sorted(OPERATION_TYPES)!r}}}\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    registry = build_registry("call_shape_extensions")
    assert set(registry.operations) == set(OPERATION_TYPES)

    default_discovery_calls = []
    def extension_present_registry():
        default_discovery_calls.append(True)
        return registry
    monkeypatch.setattr(sys.modules[__name__], "build_registry", extension_present_registry)
    examples_root = tmp_path / "example inputs"
    examples_root.mkdir()
    for name in sorted(OPERATION_TYPES):
        assert callable(registry.require_operation(name))
        test_typed_operation_call_examples(name, examples_root)
    assert not default_discovery_calls


def test_runtime_links_and_values_are_not_portable_json(tmp_path):
    examples = operation_inputs(tmp_path)
    with pytest.raises(ContractError, match="INVALID_JSON"):
        canonical_bytes(examples["FinalizeWindow"]["decoded"])
    assert examples["AssembleExport"]["results"][0]["status"] == "planned"
    assert examples["ExpandNativeRender"]["models"].model.as_list() == ["synthetic-model", 0]
