import inspect
import subprocess
import sys
from typing import get_type_hints

import pytest

from kmin_video_director.contracts.worker import OPERATION_TYPES
from kmin_video_director.registration import build_registry
from tests.contracts.worker_examples import operation_inputs


def test_real_handler_signatures_and_no_io_examples(tmp_path):
    registry = build_registry()
    expected = {'ProbeMedia', 'NormalizeMedia', 'PlanWindows', 'PrepareWindow', 'AssembleExport'}
    assert set(registry.operations) == expected
    examples = operation_inputs(tmp_path)
    for name in expected:
        implementation = registry.require_operation(name)
        actual = inspect.signature(implementation)
        protocol = inspect.signature(OPERATION_TYPES[name].__call__)
        assert list(actual.parameters) == list(protocol.parameters)[1:]
        assert actual.parameters['context'].kind == inspect.Parameter.KEYWORD_ONLY
        assert get_type_hints(implementation) == get_type_hints(OPERATION_TYPES[name].__call__)
        actual.bind(**examples[name])
    assert not list(tmp_path.iterdir())
    with pytest.raises(ValueError, match='UNSUPPORTED_CAPABILITY'):
        registry.require_operation('ExpandNativeRender')


def test_all_owned_nodes_import_without_optional_packages_or_backend_probe():
    script = '''
import importlib.abc, importlib.util, subprocess, sys
from pathlib import Path
class Reject(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'comfy','torch','numpy','av','cv2','PIL','jsonschema','server','folder_paths'}:
            raise ImportError('Optional package deliberately absent')
def forbidden(*args, **kwargs):
    raise AssertionError('Package import/INPUT_TYPES must not probe media or launch a backend')
subprocess.Popen = forbidden
sys.meta_path.insert(0, Reject())
spec = importlib.util.spec_from_file_location('kvd_pack', Path('__init__.py'), submodule_search_locations=[str(Path.cwd())])
pack = importlib.util.module_from_spec(spec); sys.modules[spec.name] = pack
spec.loader.exec_module(pack)
assert len(pack.NODE_CLASS_MAPPINGS) == 12
for node in pack.NODE_CLASS_MAPPINGS.values(): node.INPUT_TYPES()
assert len(pack.REGISTRY.operations) == 5
'''
    done = subprocess.run([sys.executable, '-I', '-c', script], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr


def test_port_closure_without_executing_nodes():
    from kmin_video_director.nodes.media.media_nodes import NODE_CLASS_MAPPINGS as nodes
    edges = [('KVD_ProbeMedia', 'source_media', 'KVD_NormalizeMedia', 'source_media'),
        ('KVD_ProbeMedia', 'probe', 'KVD_MediaProject', 'probe'),
        ('KVD_NormalizeMedia', 'normalized', 'KVD_MediaProject', 'normalized'),
        ('KVD_MediaProject', 'project', 'KVD_PlanWindows', 'project'),
        ('KVD_MediaProject', 'render_profile', 'KVD_PlanWindows', 'render_profile'),
        ('KVD_PlanWindows', 'project', 'KVD_SelectWindow', 'project'),
        ('KVD_SelectWindow', 'window', 'KVD_PrepareWindow', 'window'),
        ('KVD_SelectWindow', 'canonical_media', 'KVD_PrepareWindow', 'canonical_media'),
        ('KVD_SelectWindow', 'spatial', 'KVD_PrepareWindow', 'spatial'),
        ('KVD_SelectResults', 'project', 'KVD_AssembleExport', 'project')]
    for source, out, destination, port in edges:
        output_type = nodes[source].RETURN_TYPES[nodes[source].RETURN_NAMES.index(out)]
        assert output_type == nodes[destination].INPUT_TYPES()['required'][port][0]
    for cls in nodes.values():
        inputs = cls.INPUT_TYPES()
        required = inputs['required']
        inspect.signature(getattr(cls, cls.FUNCTION)).bind(None, **{k: object() for k in required})
        assert len(cls.RETURN_NAMES) == len(cls.RETURN_TYPES)
