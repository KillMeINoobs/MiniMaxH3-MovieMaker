import inspect
import json
from pathlib import Path
import subprocess
import sys
from typing import get_type_hints

import pytest

from kmin_video_director.contracts.worker import OPERATION_TYPES
from kmin_video_director.errors import ContractError
from kmin_video_director.registration import ExtensionRegistry, build_registry
from tests.contracts.worker_examples import operation_inputs
from tests.imports.test_registration import pack_with_extension


MEDIA_OPERATIONS = {'ProbeMedia', 'NormalizeMedia', 'PlanWindows', 'PrepareWindow', 'AssembleExport'}
MEDIA_NODES = {'KVD_ProbeMedia', 'KVD_NormalizeMedia', 'KVD_MediaProject', 'KVD_PlanWindows',
    'KVD_SelectWindow', 'KVD_PrepareWindow', 'KVD_SelectResults', 'KVD_AssembleExport'}
FOUNDATION_NODES = {'KVD_ProjectJSON', 'KVD_LoadProject', 'KVD_SaveProject', 'KVD_ValidateProject'}


def assert_media_handler_signatures(registry, tmp_path):
    expected = MEDIA_OPERATIONS
    assert expected <= set(registry.operations)
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


def test_real_handler_signatures_and_no_io_examples(tmp_path):
    assert_media_handler_signatures(build_registry(), tmp_path)


@pytest.mark.parametrize('name', sorted(OPERATION_TYPES))
def test_explicit_empty_registry_rejects_unsupported_operations(name):
    registry = ExtensionRegistry({}, {}, {}, ())
    with pytest.raises(ContractError) as raised:
        registry.require_operation(name)
    assert raised.value.code == 'UNSUPPORTED_CAPABILITY'
    assert raised.value.details['operation'] == name


def import_pack_metadata(pack_root):
    script = (f'required_node_ids = {sorted(FOUNDATION_NODES | MEDIA_NODES)!r}\n'
        f'required_operations = {sorted(MEDIA_OPERATIONS)!r}\n') + '''
import importlib.abc, importlib.util, json, subprocess, sys
from pathlib import Path
blocked_roots = {'comfy','torch','numpy','av','cv2','PIL','jsonschema','server','folder_paths',
                 'transformers','safetensors','onnxruntime'}
class Reject(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in blocked_roots:
            raise ImportError('Optional package deliberately absent')
def forbidden(*args, **kwargs):
    raise AssertionError('Package import/INPUT_TYPES must not probe media or launch a backend')
subprocess.Popen = forbidden
sys.meta_path.insert(0, Reject())
spec = importlib.util.spec_from_file_location('kvd_pack', Path('__init__.py'), submodule_search_locations=[str(Path.cwd())])
pack = importlib.util.module_from_spec(spec); sys.modules[spec.name] = pack
spec.loader.exec_module(pack)
print('Observed metadata:', len(pack.NODE_CLASS_MAPPINGS), 'nodes,', len(pack.REGISTRY.operations), 'operations')
assert set(required_node_ids) <= set(pack.NODE_CLASS_MAPPINGS), ('Missing required nodes', sorted(set(required_node_ids) - set(pack.NODE_CLASS_MAPPINGS)))
assert set(required_operations) <= set(pack.REGISTRY.operations), ('Missing required media operations', sorted(set(required_operations) - set(pack.REGISTRY.operations)))
for class_id, node in pack.NODE_CLASS_MAPPINGS.items():
    assert isinstance(node.INPUT_TYPES(), dict), class_id
assert not blocked_roots.intersection(name.split('.')[0] for name in sys.modules)
print(json.dumps({'node_ids': sorted(pack.NODE_CLASS_MAPPINGS), 'operation_ids': sorted(pack.REGISTRY.operations)}))
'''
    done = subprocess.run([sys.executable, '-I', '-c', script], cwd=pack_root, capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    return json.loads(done.stdout.splitlines()[-1])


def test_all_owned_nodes_import_without_optional_packages_or_backend_probe():
    import_pack_metadata(Path(__file__).resolve().parents[2])


def pack_with_guard_extension(tmp_path, *, eager=None):
    # Add only missing operations so this fixture also works in a legitimate
    # combined pack. Every supplied callback is an execution-failing guard.
    extra_operations = sorted(set(OPERATION_TYPES) - set(build_registry().operations))
    source = '''
class MetadataGuardNode:
    FUNCTION = 'execute'
    RETURN_TYPES = ('STRING',)
    RETURN_NAMES = ('value',)
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'value': ('STRING',)}}
    def execute(self, value):
        raise AssertionError('Metadata checks must not execute a node')
def execution_guard(*args, **kwargs):
    raise AssertionError('Metadata checks must not execute an operation')
NODE_CLASS_MAPPINGS = {f'KVD_MediaImportExtension{i}': MetadataGuardNode for i in range(13)}
'''
    source += f'OPERATIONS = {{name: execution_guard for name in {extra_operations!r}}}\n'
    if eager == 'input_types':
        source = source.replace("        return {'required'", "        import torch\n        return {'required'")
    elif eager == 'import':
        source = 'import torch\n' + source
    return pack_with_extension(tmp_path, source)


def test_media_signature_check_accepts_additional_guard_handlers(tmp_path, monkeypatch):
    core = build_registry()
    package = tmp_path / 'media_guard_handlers'
    package.mkdir()
    (package / '__init__.py').write_text('', encoding='utf-8')
    (package / 'guard_nodes.py').write_text(
        "def execution_guard(*args, **kwargs):\n"
        "    raise AssertionError('Signature checks must not execute an operation')\n"
        "OPERATIONS = {name: execution_guard for name in "
        "('BuildControl', 'CompileWindowPrompt', 'ExpandNativeRender', 'FinalizeWindow')}\n", encoding='utf-8')
    monkeypatch.syspath_prepend(str(tmp_path))
    extra = build_registry('media_guard_handlers')
    registry = ExtensionRegistry(core.nodes, core.display_names,
        {**core.operations, **extra.operations}, core.modules + extra.modules)
    assert callable(registry.require_operation('ExpandNativeRender'))
    examples_root = tmp_path / 'no-io examples'
    examples_root.mkdir()
    assert_media_handler_signatures(registry, examples_root)


def test_media_import_check_accepts_extra_owned_nodes_and_handlers(tmp_path):
    report = import_pack_metadata(pack_with_guard_extension(tmp_path))
    assert {f'KVD_MediaImportExtension{i}' for i in range(13)} <= set(report['node_ids'])
    assert set(OPERATION_TYPES) <= set(report['operation_ids'])


@pytest.mark.parametrize('class_id', sorted(FOUNDATION_NODES | MEDIA_NODES))
def test_media_import_check_rejects_missing_required_class(tmp_path, class_id):
    pack = pack_with_guard_extension(tmp_path)
    entry = pack / '__init__.py'
    entry.write_text(entry.read_text(encoding='utf-8') +
        f'\nNODE_CLASS_MAPPINGS.pop({class_id!r})\n', encoding='utf-8')
    with pytest.raises(AssertionError, match=f'Missing required nodes.*{class_id}'):
        import_pack_metadata(pack)


@pytest.mark.parametrize('name', sorted(MEDIA_OPERATIONS))
def test_media_signature_check_rejects_missing_required_handler(tmp_path, name):
    core = build_registry()
    registry = ExtensionRegistry(core.nodes, core.display_names,
        {key: value for key, value in core.operations.items() if key != name}, core.modules)
    with pytest.raises(AssertionError):
        assert_media_handler_signatures(registry, tmp_path)


@pytest.mark.parametrize('name', sorted(MEDIA_OPERATIONS))
def test_media_import_check_rejects_missing_required_handler(tmp_path, name):
    pack = pack_with_guard_extension(tmp_path)
    entry = pack / '__init__.py'
    entry.write_text(entry.read_text(encoding='utf-8') +
        "\nfrom dataclasses import replace\n"
        f"REGISTRY = replace(REGISTRY, operations={{key: value for key, value in REGISTRY.operations.items() if key != {name!r}}})\n",
        encoding='utf-8')
    with pytest.raises(AssertionError, match=f'Missing required media operations.*{name}'):
        import_pack_metadata(pack)


@pytest.mark.parametrize('stage', ['import', 'input_types'])
def test_media_import_check_rejects_eager_optional_backend(tmp_path, stage):
    pack = pack_with_guard_extension(tmp_path, eager=stage)
    with pytest.raises(AssertionError, match='Optional package deliberately absent'):
        import_pack_metadata(pack)


def test_port_closure_without_executing_nodes():
    from kmin_video_director.nodes.media.media_nodes import NODE_CLASS_MAPPINGS as nodes
    assert MEDIA_NODES <= set(nodes)
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
