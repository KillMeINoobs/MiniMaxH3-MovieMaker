"""Portable artifact/actual owned-schema checks; never load or queue a workflow.

Media socket declarations below are dependency descriptions at the pinned
pending candidate, not installed classes or implementations in this checkout.
"""
import json
from pathlib import Path

import pytest

from kmin_video_director.registration import build_registry

ROOT=Path(__file__).resolve().parents[2]
MEDIA={
    'KVD_ProbeMedia':({},('KVD_PROBE','KVD_MEDIA','STRING')),
    'KVD_NormalizeMedia':({'source_media':'KVD_MEDIA'},('KVD_NORMALIZED','KVD_MEDIA','KVD_AUDIO_TIMELINE','STRING')),
    'KVD_MediaProject':({'probe':'KVD_PROBE','normalized':'KVD_NORMALIZED','render_profile':'KVD_RENDER_PROFILE'},('KVD_PROJECT','KVD_RENDER_PROFILE','STRING')),
    'KVD_PlanWindows':({'project':'KVD_PROJECT','render_profile':'KVD_RENDER_PROFILE'},('KVD_PROJECT','KVD_WINDOW_PLAN','STRING')),
    'KVD_SelectWindow':({'project':'KVD_PROJECT'},('KVD_WINDOW','KVD_MEDIA','KVD_SPATIAL','STRING')),
    'KVD_PrepareWindow':({'window':'KVD_WINDOW','canonical_media':'KVD_MEDIA','spatial':'KVD_SPATIAL'},('KVD_PREPARED','KVD_MEDIA','STRING')),
    'KVD_AssembleExport':({'project':'KVD_PROJECT','audio_timeline':'KVD_AUDIO_TIMELINE'},('KVD_RENDER_RESULT','KVD_MEDIA','STRING')),
}


def read(name):
    return json.loads((ROOT/'workflows'/name).read_text(encoding='utf-8'))


@pytest.mark.parametrize('name,count,link_count',[('m1_short_v2v.json',22,41),('m1_canny_preview.json',10,15)])
def test_diagnostic_workflow_closes_links_and_matches_actual_owned_native_metadata(name,count,link_count):
    workflow=read(name)
    registry=build_registry()
    native=json.loads((ROOT/'tests/adapters/native_schema_fixture.json').read_text())['schemas']
    nodes={n['id']:n for n in workflow['nodes']}
    assert len(nodes)==count and len(workflow['links'])==link_count
    assert workflow['extra']['kvd']['status']=='diagnostic_only'
    assert workflow['extra']['kvd']['media_integrated'] is False
    assert workflow['extra']['kvd']['queue_accepted'] is False
    for n in nodes.values():
        cls=n['type']
        if cls in registry.nodes:
            actual=registry.nodes[cls]
            fields=actual.INPUT_TYPES()
            outputs=actual.RETURN_TYPES
            if getattr(actual,'OUTPUT_NODE',False): assert n['mode']==2
        elif cls in native: fields=native[cls]['input'];outputs=native[cls]['output']
        elif cls=='PreviewImage':
            # Source-declared in pinned daeb nodes.py:1740, not in the 32-class capture.
            fields={'required':{'images':('IMAGE',)}};outputs=()
            assert n['mode']==2
        else:
            inputs,outputs=MEDIA[cls]
            assert cls not in registry.nodes  # Dependency is intentionally not adopted.
            assert {p['name']:p['type'] for p in n['inputs']}==inputs
            assert tuple(p['type'] for p in n['outputs'])==outputs
            continue
        assert tuple(p['type'] for p in n['outputs'])==tuple(outputs)
        ports={};widgets=[]
        for group in ('required','optional'):
            for key,port in fields.get(group,{}).items():
                kind=port[0]
                if isinstance(kind,list) or kind in ('STRING','INT','FLOAT','BOOLEAN','COMBO'):
                    widgets.append((key,port))
                else: ports[key]=kind
        assert {p['name']:p['type'] for p in n['inputs']}==ports
        assert len(n['widgets_values'])==len(widgets)
        for (key,_),value in zip(widgets,n['widgets_values']):
            if key in ('project_root','ffmpeg_path','ffprobe_path','native_schema_file'):
                assert value==''
    seen=set()
    for id,source,slot,target,input_slot,kind in workflow['links']:
        assert id not in seen;seen.add(id)
        a=nodes[source]['outputs'][slot];b=nodes[target]['inputs'][input_slot]
        assert a['type']==b['type']==kind and b['link']==id and id in a['links']
    assert workflow['last_node_id']==max(nodes) and workflow['last_link_id']==max(seen)


def test_preparation_preview_has_no_generation_weights_profile_or_sampler_ancestor():
    w=read('m1_canny_preview.json')
    classes={n['type'] for n in w['nodes']}
    assert classes=={'KVD_ProbeMedia','KVD_NormalizeMedia','KVD_MediaProject','KVD_ControlSettings',
        'KVD_PlanWindows','KVD_SelectWindow','KVD_PrepareWindow','KVD_BuildControl','KVD_ControlPreview','PreviewImage'}
    assert w['extra']['kvd']['generation_dependencies']==[]
    project=next(n for n in w['nodes'] if n['type']=='KVD_MediaProject')
    assert next(p for p in project['inputs'] if p['name']=='render_profile')['link'] is None
    # The shape profile comes from existing media Project output, never H3Profile.
    for _,source,slot,target,input_slot,kind in w['links']:
        if kind=='KVD_RENDER_PROFILE': assert source==project['id'] and slot==1


def test_generation_variant_separates_control_and_models_and_keeps_authored_prompt_visible():
    w=read('m1_short_v2v.json')
    registry=build_registry()
    nodes={n['id']:n for n in w['nodes']}
    expand=next(n for n in nodes.values() if n['type']=='KVD_ExpandNativeRender')
    incoming={nodes[source]['type']:kind for _,source,slot,target,input_slot,kind in w['links'] if target==expand['id']}
    assert incoming['KVD_BuildControl']=='KVD_CONTROL'
    assert incoming['UNETLoader']=='MODEL' and incoming['CLIPLoader']=='CLIP' and incoming['ModelPatchLoader']=='MODEL_PATCH'
    assert not set(p['name'] for p in expand['inputs']) & {'source_video','ref_images','ref_videos','audio_guide','mask'}
    prompt=next(n for n in nodes.values() if n['type']=='KVD_CompileWindowPrompt')
    assert registry.nodes[prompt['type']].INPUT_TYPES()['required']['prompt'][1]['multiline'] is True
    assert prompt['widgets_values']==['']  # Human authors the exact text before generation.
