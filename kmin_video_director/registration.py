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
    def import_owned(name):
        try:
            return importlib.import_module(name)
        except ImportError:
            fail("EXTENSION_IMPORT_ERROR", "An owned module cannot be imported; optional backends must be loaded lazily.",
                 details={"module": name})
    root = import_owned(package)
    def walk(owned_package):
        for info in sorted(pkgutil.iter_modules(owned_package.__path__, owned_package.__name__ + ".")):
            if info.ispkg:
                yield from walk(import_owned(info.name))
            elif info.name.endswith("_nodes"):
                yield info.name
    modules = sorted(walk(root))
    nodes, labels, operations = {}, {}, {}
    for name in modules:
        module = import_owned(name)
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
