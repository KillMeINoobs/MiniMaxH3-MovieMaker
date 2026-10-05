"""Malformed metadata rejection; tiny synthetic inputs, no native execution."""
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import types

import pytest

from kmin_video_director.adapters.native_h3 import profile as native_profile
from kmin_video_director.adapters.native_h3.checkpoints import read_header
from kmin_video_director.adapters.native_h3.graph import expand_native_render
from kmin_video_director.adapters.native_h3.schema import read_handoff
from kmin_video_director.contracts import ContractError, digest_bytes
from kmin_video_director.contracts.worker import CancellationFlag, OperationContext
from tests.adapters.test_native_graph import CORE, setup


@pytest.fixture
def forbidden_builder(monkeypatch):
    calls = []
    package = types.ModuleType('comfy_execution')
    package.__path__ = []
    module = types.ModuleType('comfy_execution.graph_utils')

    class ForbiddenBuilder:
        def __init__(self, *args, **kwargs):
            calls.append(True)
            raise AssertionError('Malformed metadata must be rejected before GraphBuilder.')

    module.GraphBuilder = ForbiddenBuilder
    monkeypatch.setitem(sys.modules, package.__name__, package)
    monkeypatch.setitem(sys.modules, module.__name__, module)
    yield calls
    assert calls == []


def write_nonfinite_schema(ctx, schemas, token):
    schemas['BasicScheduler']['input']['required']['steps'][1]['min'] = 'NONFINITE_SCHEMA_TOKEN'
    text = json.dumps({'runtime': {'core_commit': CORE}, 'schemas': schemas})
    Path(ctx.versions['native_schema_file']).write_text(
        text.replace('"NONFINITE_SCHEMA_TOKEN"', token), encoding='utf-8')


@pytest.mark.parametrize('token', ['1e999', '-1e999', 'NaN', 'Infinity', '-Infinity'])
def test_review_h4_nonfinite_schema_option_is_typed_before_builder(tmp_path, forbidden_builder, token):
    w, p, models, control, prompt, ctx, schemas, _ = setup(tmp_path)
    write_nonfinite_schema(ctx, schemas, token)
    with pytest.raises(ContractError, match='MODEL_INCOMPATIBLE') as error:
        expand_native_render(w, p, models, control, prompt, None, context=ctx)
    assert error.value.code == 'MODEL_INCOMPATIBLE' and error.value.stage == 'prepare'
    assert 'finite' in error.value.message.lower()
    assert str(tmp_path) not in str(error.value) and token not in error.value.message


def test_review_h4_schema_is_rejected_before_any_fingerprinting(tmp_path, monkeypatch, forbidden_builder):
    w, p, models, control, prompt, ctx, schemas, _ = setup(tmp_path)
    write_nonfinite_schema(ctx, schemas, '1e999')
    calls = []

    def forbidden_fingerprint(schema):
        calls.append(True)
        raise AssertionError('Invalid schema options must not reach fingerprinting.')

    monkeypatch.setattr(native_profile, 'schema_digest', forbidden_fingerprint)
    with pytest.raises(ContractError, match='MODEL_INCOMPATIBLE'):
        expand_native_render(w, p, models, control, prompt, None, context=ctx)
    assert calls == []


@pytest.mark.parametrize('number', [float('inf'), float('-inf'), float('nan')], ids=['inf', 'negative-inf', 'nan'])
def test_review_h4_nested_schema_options_have_typed_fingerprint_rejection(number):
    schema = {'input': {'required': {'steps': ['INT', {'nested': {'bounds': [0, number]}}]}},
              'output': ['SIGMAS']}
    with pytest.raises(ContractError, match='MODEL_INCOMPATIBLE') as error:
        native_profile.schema_digest(schema)
    assert 'finite' in error.value.message.lower()


def test_finite_installed_schemas_preserve_canonical_fingerprints(tmp_path):
    original = os.environ.get('KVD_NATIVE_SCHEMA_CAPTURE')
    preview = os.environ.get('KVD_PREVIEWIMAGE_SCHEMA_CAPTURE')
    if not original or not preview:
        pytest.skip('Hash-verified installed native metadata was not supplied; no substitute capture.')
    raw = Path(original).read_bytes()
    supplement = Path(preview).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == 'b5d9ffab1130ebaf98cf1cfecda529e7c8a3b0c19cd57894e982ed12142ed34d'
    assert hashlib.sha256(supplement).hexdigest() == '0751c1d78c8ba97a23a8167de253f63766ce43b041e1e866820fa4463081916c'
    capture = json.loads(raw.decode('utf-8-sig'))
    capture['schemas'].update(json.loads(supplement.decode('utf-8-sig')))
    assert len(capture['schemas']) == 33
    path = tmp_path / 'finite-captured-schemas.json'
    path.write_text(json.dumps(capture), encoding='utf-8')
    schemas, core = read_handoff(OperationContext(tmp_path, CancellationFlag(), {'native_schema_file': str(path)}))
    assert schemas == capture['schemas'] and core == CORE
    for schema in schemas.values():
        relevant = {key: schema.get(key) for key in ('input', 'input_order', 'output', 'output_is_list')}
        expected = digest_bytes(json.dumps(relevant, ensure_ascii=False, sort_keys=True,
            separators=(',', ':'), allow_nan=False).encode('utf-8'))
        assert native_profile.schema_digest(schema) == expected


def write_tiny_header(path, dtype):
    header = {'tensor': {'dtype': dtype, 'shape': [1], 'data_offsets': [0, 4]}}
    payload = json.dumps(header).encode('utf-8')
    path.write_bytes(struct.pack('<Q', len(payload)) + payload + bytes(4))
    return header


@pytest.mark.parametrize('dtype', [['F32'], {'private-dtype-value': 'F32'}, None, True, 1, 'UNKNOWN'],
                         ids=['list', 'object', 'null', 'bool', 'number', 'unknown-string'])
def test_review_h5_malformed_dtype_is_typed_and_redacted(tmp_path, dtype):
    path = tmp_path / 'tiny-synthetic-header.bin'
    write_tiny_header(path, dtype)
    ctx = OperationContext(tmp_path, CancellationFlag(), {})
    with pytest.raises(ContractError, match='MODEL_INCOMPATIBLE') as error:
        read_header(path, context=ctx)
    assert error.value.code == 'MODEL_INCOMPATIBLE' and error.value.stage == 'prepare'
    assert str(path) not in str(error.value) and 'private-dtype-value' not in str(error.value)


def test_valid_tiny_header_keeps_content_fingerprint(tmp_path):
    path = tmp_path / 'tiny-synthetic-header.bin'
    expected = write_tiny_header(path, 'F32')
    header, fingerprint = read_header(path, context=OperationContext(tmp_path, CancellationFlag(), {}))
    assert header == expected
    assert fingerprint == {'digest': digest_bytes(path.read_bytes()), 'byte_size': path.stat().st_size}
