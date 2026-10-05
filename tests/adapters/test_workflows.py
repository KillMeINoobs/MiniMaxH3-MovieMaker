"""Merged node metadata and immutable native handoffs; never load/queue."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path

import pytest
from kmin_video_director.registration import build_registry

ROOT = Path(__file__).resolve().parents[2]
CM = '69ed44577550b8545a40cc3209a488d9fcd13fda'
CORE = 'daeb5e53681e2b10a3f0727d9ec5bc90784bee10'
BASE = 'minimax_h3_ref2va_pruned_int8_convrot.safetensors'


def read(name):
    return json.loads((ROOT / 'workflows' / name).read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def actual_native_schemas():
    specifications = (
        ('KVD_NATIVE_SCHEMA_CAPTURE', 'b5d9ffab1130ebaf98cf1cfecda529e7c8a3b0c19cd57894e982ed12142ed34d'),
        ('KVD_PREVIEWIMAGE_SCHEMA_CAPTURE', '0751c1d78c8ba97a23a8167de253f63766ce43b041e1e866820fa4463081916c'),
        ('KVD_PREVIEWIMAGE_SCHEMA_RECEIPT', 'b99b8762014943eb58dd38a75787422ebfbe799fc63a12664269eee3bb020f03'),
    )
    captures = []
    for variable, digest in specifications:
        path = Path(os.environ.get(variable, ''))
        if not path.is_file():
            pytest.skip('Actual read-only native handoff not supplied: ' + variable)
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest
        captures.append(json.loads(data))
    native, preview, receipt = captures
    assert native['runtime']['core_commit'] == receipt['core_revision'] == CORE
    assert receipt['http_status'] == 200 and receipt['queue_running'] == receipt['queue_pending'] == 0
    assert len(native['schemas']) == 32 and set(preview) == {'PreviewImage'}
    return {**native['schemas'], **preview}


def validate_workflow(workflow, native):
    registry = build_registry()
    nodes = {node['id']: node for node in workflow['nodes']}
    assert len(nodes) == len(workflow['nodes'])
    resource_gates = []
    for node in nodes.values():
        class_id = node['type']
        if class_id in registry.nodes:
            actual = registry.nodes[class_id]
            fields, outputs = actual.INPUT_TYPES(), actual.RETURN_TYPES
            names = getattr(actual, 'RETURN_NAMES', outputs)
            output_node = getattr(actual, 'OUTPUT_NODE', False)
        else:
            actual = native[class_id]
            fields, outputs, names = actual['input'], actual['output'], actual['output_name']
            output_node = actual['output_node']
        if output_node:
            assert node['mode'] == 2
        assert tuple(p['type'] for p in node['outputs']) == tuple(outputs)
        assert tuple(p['name'] for p in node['outputs']) == tuple(names)
        assert [p['slot_index'] for p in node['outputs']] == list(range(len(outputs)))
        ports, widgets, required = {}, [], set()
        for group in ('required', 'optional'):
            for key, specification in fields.get(group, {}).items():
                kind = specification[0]
                if isinstance(kind, list) or kind in ('STRING', 'INT', 'FLOAT', 'BOOLEAN', 'COMBO'):
                    widgets.append((key, specification))
                    continue
                else:
                    ports[key] = kind
                if group == 'required':
                    required.add(key)
        # Reviewed frontend1.53.6 creates nonwidgets, then every widget socket.
        # Author them explicitly so load/serialize cannot silently add inputs.
        for key, specification in widgets:
            kind = specification[0]
            ports[key] = kind if isinstance(kind, str) else 'COMBO'
            assert next(p for p in node['inputs'] if p['name'] == key)['widget'] == {'name': key}
        assert {p['name']: p['type'] for p in node['inputs']} == ports
        assert [p['name'] for p in node['inputs']] == list(ports)
        assert len(node['widgets_values']) == len(widgets)
        for (key, specification), value in zip(widgets, node['widgets_values']):
            kind = specification[0]
            options = specification[1] if len(specification) > 1 else {}
            choices = kind if isinstance(kind, list) else options.get('options') if kind == 'COMBO' else None
            if choices is not None and value not in choices:
                # Preserve the real absent-resource gate, without changing enums.
                assert (class_id, key, value) == ('UNETLoader', 'unet_name', BASE)
                resource_gates.append((class_id, key, value))
            elif kind in ('STRING', 'COMBO'):
                assert isinstance(value, str)
            elif kind in ('INT', 'FLOAT'):
                assert (type(value) is int) if kind == 'INT' else (type(value) in (int, float))
                assert value >= options.get('min', value) and value <= options.get('max', value)
            elif kind == 'BOOLEAN':
                assert type(value) is bool
            if key in ('project_root', 'ffmpeg_path', 'ffprobe_path', 'native_schema_file'):
                assert value == ''
        assert all(p['link'] is not None for p in node['inputs'] if p['name'] in required)
    links = {link[0]: link for link in workflow['links']}
    assert len(links) == len(workflow['links'])
    for id, source, slot, target, input_slot, kind in links.values():
        output, input = nodes[source]['outputs'][slot], nodes[target]['inputs'][input_slot]
        assert output['type'] == input['type'] == kind
        assert input['link'] == id and id in output['links']
    for node in nodes.values():
        for i, port in enumerate(node['inputs']):
            if port['link'] is not None:
                assert links[port['link']][3:5] == [node['id'], i]
        for i, port in enumerate(node['outputs']):
            expected = {id for id, s, slot, *_ in links.values() if (s, slot) == (node['id'], i)}
            assert set(port['links'] or ()) == expected
    assert workflow['last_node_id'] == max(nodes) and workflow['last_link_id'] == max(links)
    return resource_gates


@pytest.mark.parametrize('name,count,links', [('m1_short_v2v.json', 23, 43), ('m1_canny_preview.json', 10, 15)])
def test_diagnostics_match_actual_merged_and_native_metadata(name, count, links, actual_native_schemas):
    workflow = read(name)
    assert len(workflow['nodes']) == count and len(workflow['links']) == links
    metadata = workflow['extra']['kvd']
    assert metadata['status'] == 'diagnostic_only' and metadata['checked_common'] == CM
    assert metadata['media_integrated'] is True and metadata['queue_accepted'] is False
    assert metadata['gpu'] == metadata['human_result'] == 'not_performed'
    gates = validate_workflow(workflow, actual_native_schemas)
    assert gates == ([('UNETLoader', 'unet_name', BASE)] if count == 23 else [])


@pytest.mark.parametrize('fault', ['required_link', 'output_slot', 'unknown_class', 'bad_enum', 'bad_literal',
                                 'missing_widget', 'wrong_widget', 'widget_type', 'widget_order'])
def test_schema_preflight_rejects_broken_artifact(fault, actual_native_schemas):
    workflow = deepcopy(read('m1_canny_preview.json'))
    if fault == 'required_link': workflow['nodes'][-1]['inputs'][0]['link'] = None
    elif fault == 'output_slot': workflow['links'][-1][2] = 1
    elif fault == 'unknown_class': workflow['nodes'][-1]['type'] = 'FictionalPreview'
    elif fault == 'bad_enum': workflow['nodes'][3]['widgets_values'][0] = 'pose'
    elif fault == 'bad_literal': workflow['nodes'][3]['widgets_values'][1] = 5
    elif fault == 'missing_widget': workflow['nodes'][0]['inputs'].pop()
    elif fault == 'wrong_widget': workflow['nodes'][0]['inputs'][0]['widget']['name'] = 'wrong'
    elif fault == 'widget_type': workflow['nodes'][0]['inputs'][0]['type'] = 'INT'
    elif fault == 'widget_order': workflow['nodes'][0]['inputs'].reverse()
    with pytest.raises((AssertionError, KeyError, IndexError, StopIteration)):
        validate_workflow(workflow, actual_native_schemas)


def test_preparation_preview_has_no_generation_weights_profile_or_sampler_ancestor():
    workflow = read('m1_canny_preview.json')
    classes = {node['type'] for node in workflow['nodes']}
    assert classes == {'KVD_ProbeMedia', 'KVD_NormalizeMedia', 'KVD_MediaProject', 'KVD_ControlSettings',
        'KVD_PlanWindows', 'KVD_SelectWindow', 'KVD_PrepareWindow', 'KVD_BuildControl', 'KVD_ControlPreview', 'PreviewImage'}
    assert workflow['extra']['kvd']['generation_dependencies'] == []
    project = next(n for n in workflow['nodes'] if n['type'] == 'KVD_MediaProject')
    assert next(p for p in project['inputs'] if p['name'] == 'render_profile')['link'] is None
    for _, source, slot, _, _, kind in workflow['links']:
        if kind == 'KVD_RENDER_PROFILE': assert source == project['id'] and slot == 1


def test_generation_path_uses_current_results_array_and_preserves_authored_prompt():
    workflow = read('m1_short_v2v.json')
    registry = build_registry()
    nodes = {n['id']: n for n in workflow['nodes']}
    by_class = {n['type']: n for n in nodes.values()}
    expand = by_class['KVD_ExpandNativeRender']
    incoming = {nodes[source]['type']: kind for _, source, _, target, _, kind in workflow['links'] if target == expand['id']}
    assert incoming['KVD_BuildControl'] == 'KVD_CONTROL'
    assert incoming['UNETLoader'] == 'MODEL' and incoming['CLIPLoader'] == 'CLIP' and incoming['ModelPatchLoader'] == 'MODEL_PATCH'
    assert not {p['name'] for p in expand['inputs']} & {'source_video', 'ref_images', 'ref_videos', 'audio_guide', 'mask'}
    prompt = by_class['KVD_CompileWindowPrompt']
    assert registry.nodes[prompt['type']].INPUT_TYPES()['required']['prompt'][1]['multiline'] is True
    assert prompt['widgets_values'] == ['']
    selection = by_class['KVD_SelectResults']
    assert selection['widgets_values'] == ['[]']
    finalizer = by_class['KVD_FinalizeWindow']
    input = next(p for p in selection['inputs'] if p['name'] == 'results_json')
    link = next(link for link in workflow['links'] if link[0] == input['link'])
    assert link[1:3] == [finalizer['id'], 3] and link[-1] == 'STRING'
    for name in ('KVD_AssembleExport', 'KVD_SaveProject'):
        input = next(p for p in by_class[name]['inputs'] if p['name'] == 'project')
        link = next(link for link in workflow['links'] if link[0] == input['link'])
        assert link[1:3] == [selection['id'], 0]
