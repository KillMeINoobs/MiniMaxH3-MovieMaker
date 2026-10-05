"""Deterministic discovery of owned *_nodes modules; no optional model imports."""
import importlib
import pkgutil
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Callable

from .errors import fail
from .contracts.worker import OPERATION_TYPES


@dataclass(frozen=True)
class ExtensionRegistry:
    nodes: Mapping[str, type]
    display_names: Mapping[str, str]
    operations: Mapping[str, Callable]
    modules: tuple[str, ...]

    def require_operation(self, name):
        if name not in self.operations:
            fail("UNSUPPORTED_CAPABILITY", "No implementation is registered for this operation.", details={"operation": name})
        return self.operations[name]


def build_registry(package=None):
    package = package or __package__ + ".nodes"
    root = importlib.import_module(package)
    modules = sorted(info.name for info in pkgutil.walk_packages(root.__path__, root.__name__ + ".")
                     if not info.ispkg and info.name.endswith("_nodes"))
    nodes, labels, operations = {}, {}, {}
    for name in modules:
        module = importlib.import_module(name)
        owned = getattr(module, "NODE_CLASS_MAPPINGS", {})
        if not isinstance(owned, dict):
            fail("INVALID_RECORD", "Owned node mappings must be dictionaries.")
        for id, cls in owned.items():
            if id in nodes:
                fail("DUPLICATE_ID", "Two modules register the same node class ID.", details={"class_id": id})
            if not isinstance(id, str) or not id.startswith("KVD_") or not isinstance(cls, type):
                fail("INVALID_RECORD", "Owned nodes need a KVD_ class ID and an actual class.")
            nodes[id] = cls
            labels[id] = getattr(module, "NODE_DISPLAY_NAME_MAPPINGS", {}).get(id, id)
        for op, callback in getattr(module, "OPERATIONS", {}).items():
            if op not in OPERATION_TYPES or not callable(callback):
                fail("INVALID_RECORD", "Operation registration requires a known interface and callable implementation.")
            if op in operations:
                fail("DUPLICATE_ID", "Each runtime operation has one owner.", details={"operation": op})
            operations[op] = callback
    return ExtensionRegistry(MappingProxyType(nodes), MappingProxyType(labels), MappingProxyType(operations), tuple(modules))
