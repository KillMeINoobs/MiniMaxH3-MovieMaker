import importlib
import inspect
import subprocess
import sys
from pathlib import Path

import pytest
from tests.contracts.example_data import project


def test_import_and_nodes_without_optional_dependencies():
    script = r'''
import importlib.abc, importlib.util, sys
from pathlib import Path
class Reject(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'torch','numpy','cv2','comfy','server','folder_paths','transformers','safetensors','onnxruntime','av','PIL','jsonschema'}:
            raise ImportError('Optional dependency deliberately unavailable')
sys.meta_path.insert(0, Reject())
spec = importlib.util.spec_from_file_location('kvd_pack', Path('__init__.py'), submodule_search_locations=[str(Path.cwd())])
pack = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = pack
spec.loader.exec_module(pack)
assert set(pack.NODE_CLASS_MAPPINGS) == {'KVD_ProjectJSON','KVD_LoadProject','KVD_SaveProject','KVD_ValidateProject'}
assert pack.WEB_DIRECTORY == './web'
for node in pack.NODE_CLASS_MAPPINGS.values():
    node.INPUT_TYPES()
print('import-safe: 4 actual Project nodes; optional packages absent')
'''
    done = subprocess.run([sys.executable, "-I", "-c", script], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert "import-safe" in done.stdout


def test_owned_module_discovery_and_duplicate_rejection(tmp_path, monkeypatch):
    registration = importlib.import_module("kmin_video_director.registration")
    folder = tmp_path / "owned_extensions"
    folder.mkdir()
    (folder / "__init__.py").write_text("")
    (folder / "media_nodes.py").write_text(
        "class Probe: pass\nNODE_CLASS_MAPPINGS={'KVD_TestProbe':Probe}\n"
        "NODE_DISPLAY_NAME_MAPPINGS={'KVD_TestProbe':'Test probe'}\n"
        "OPERATIONS={'ProbeMedia':lambda *args, **kwargs: None}\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    r = registration.build_registry("owned_extensions")
    assert set(r.nodes) == {"KVD_TestProbe"}
    assert callable(r.require_operation("ProbeMedia"))
    with pytest.raises(ValueError, match="UNSUPPORTED_CAPABILITY"):
        r.require_operation("BuildControl")
    (folder / "bad_nodes.py").write_text("class Bad: pass\nNODE_CLASS_MAPPINGS={'KVD_TestProbe':Bad}\n")
    importlib.invalidate_caches()
    with pytest.raises(ValueError, match="DUPLICATE_ID"):
        registration.build_registry("owned_extensions")


def test_worker_protocol_signatures_and_native_link_types():
    w = importlib.import_module("kmin_video_director.contracts.worker")
    expected = {"ProbeMedia", "NormalizeMedia", "PlanWindows", "PrepareWindow", "BuildControl",
                "CompileWindowPrompt", "ExpandNativeRender", "FinalizeWindow", "AssembleExport"}
    assert set(w.OPERATION_TYPES) == expected
    for protocol in w.OPERATION_TYPES.values():
        sig = inspect.signature(protocol.__call__)
        assert "context" in sig.parameters
        assert sig.parameters["context"].kind is inspect.Parameter.KEYWORD_ONLY
        assert sig.return_annotation is not inspect.Signature.empty
    with pytest.raises(ValueError, match="INVALID_RECORD"):
        w.NativeLink("node", -1)
    token = w.CancellationFlag()
    token.check()
    token.cancel()
    with pytest.raises(ValueError, match="CANCELLED"):
        token.check()


def test_broken_owned_child_package_is_not_silently_omitted(tmp_path, monkeypatch):
    from kmin_video_director.registration import build_registry
    folder = tmp_path / "broken_owned_extensions"
    child = folder / "broken"
    child.mkdir(parents=True)
    (folder / "__init__.py").write_text("")
    (child / "__init__.py").write_text("raise ImportError('Missing owned import')\n")
    (child / "media_nodes.py").write_text("class Probe: pass\nNODE_CLASS_MAPPINGS={'KVD_BrokenProbe':Probe}\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    with pytest.raises(ValueError, match="EXTENSION_IMPORT_ERROR"):
        build_registry("broken_owned_extensions")


def test_actual_project_nodes_cpu_io_and_reports(tmp_path):
    n = importlib.import_module("kmin_video_director.nodes.project_nodes")
    from kmin_video_director.contracts import dumps, Project
    execution = n.ProjectJSON().execute(dumps(Project.from_dict(project())))
    assert execution['ui']['kvd_report'][0]['code'] == 'STRUCTURE_VALID'
    p, text, report = execution['result']
    assert p.id == "proj-1" and '"assets_checked": false' in report
    assert n.ValidateProject().execute(p)['result'][0] == p
    _, saved, _ = n.SaveProject().execute(p, str(tmp_path), "project.kvd.json", False)['result']
    assert saved == "project.kvd.json"
    assert n.LoadProject().execute(str(tmp_path), saved)['result'][0] == p
    assert "KVD_PROJECT" in n.ValidateProject.INPUT_TYPES()["required"]["project"]
