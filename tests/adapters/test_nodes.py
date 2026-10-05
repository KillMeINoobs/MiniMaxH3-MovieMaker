"""Owned metadata and pure CPU call behavior. No native node execution or queue."""
import inspect
import json
import os
from pathlib import Path

import pytest

from kmin_video_director.contracts import ContractError, GenerationWindow, Project, RenderProfile
from kmin_video_director.contracts.worker import OPERATION_TYPES
from kmin_video_director.registration import build_registry
from kmin_video_director.nodes.h3 import h3_nodes
from kmin_video_director.adapters.native_h3.graph import OWN_SCHEMAS
from tests.contracts.example_data import project
from tests.adapters.test_native_graph import setup, native_builder


def test_four_handlers_are_actual_owned_functions_with_unchanged_call_signatures():
    registry=build_registry()
    for name in ('BuildControl','CompileWindowPrompt','ExpandNativeRender','FinalizeWindow'):
        function=registry.require_operation(name)
        actual=inspect.signature(function)
        protocol=inspect.signature(OPERATION_TYPES[name].__call__)
        assert [(p.name,p.kind) for p in actual.parameters.values()]==[(p.name,p.kind) for p in protocol.parameters.values() if p.name!='self']
        assert inspect.isfunction(function) and ('.controls.' in function.__module__ or '.native_h3.' in function.__module__)


def test_registered_node_fields_bind_real_methods_without_importing_backends():
    for name,node in h3_nodes.NODE_CLASS_MAPPINGS.items():
        fields=node.INPUT_TYPES()
        inputs={k:object() for group in ('required','optional','hidden') for k in fields.get(group,{})}
        inspect.signature(getattr(node(),node.FUNCTION)).bind(**inputs)
        assert len(node.RETURN_TYPES)==len(getattr(node,'RETURN_NAMES',node.RETURN_TYPES))
        if name in OWN_SCHEMAS:
            expected=OWN_SCHEMAS[name]
            assert tuple(node.RETURN_TYPES)==expected[2]
            if name!='KVD_FinalizeWindow':
                for group,index in (('required',0),('optional',1)):
                    assert {k:v[0] for k,v in fields.get(group,{}).items()}==expected[index]


def test_actual_authored_node_binds_visible_text_and_current_generation_key(tmp_path):
    w,p,models,control,prompt,ctx,schemas,parent=setup(tmp_path)
    authored=h3_nodes.CompileWindowPrompt().execute(w,'Visible per-window author edit.\nАвторский текст.')['result']
    wd,compiled,text=authored
    assert text==compiled.text==wd['compiled_prompt']
    data=project()
    data['windows']={w.id:w.to_dict()}
    data['render_profiles'][p['id']]=p.to_dict()
    bound=h3_nodes.BindWindow().execute(Project.from_dict(data),wd,p,control,compiled)['result']
    updated,bw=bound
    assert bw['generation_key']!=w['generation_key']
    assert updated['windows'][w.id]==bw.to_dict()
    assert updated['defaults']['prompt']==data['defaults']['prompt']
    assert updated['revision']==data['revision']+1


def test_human_profile_reports_missing_baseline_before_reading_any_checkpoint(tmp_path):
    original=Path(os.environ.get('KVD_NATIVE_SCHEMA_CAPTURE',Path(__file__).resolve().parents[2]/'.ao/primary/native-schemas.json'))
    if not original.is_file(): pytest.skip('No actual read-only native schema handoff supplied.')
    with pytest.raises(ContractError,match='MODEL_INCOMPATIBLE'):
        h3_nodes.H3Profile().execute(str(tmp_path),str(original),'canny',
                                    **{k+'_file':v for k,v in h3_nodes.DEFAULT_FILES.items()})


def test_preview_off_is_a_typed_gap_and_has_no_fake_source_passthrough(tmp_path):
    _,_,_,c,_,_,_,_=setup(tmp_path,off=True)
    with pytest.raises(ContractError,match='UNSUPPORTED_CAPABILITY'):
        h3_nodes.ControlPreview().execute(c,str(tmp_path),0)


def test_visible_control_settings_author_recipe_without_changing_prompt_or_refs(tmp_path):
    _,profile,_,_,_,_,_,_=setup(tmp_path)
    data=project()
    data['render_profiles'][profile['id']]=profile.to_dict()
    original=Project.from_dict(data)
    for mode in ('canny','off'):
        updated=h3_nodes.ControlSettings().execute(original,profile,mode,.2,.4,.6,.1,.9)['result'][0]
        spec=updated['controls'][updated['defaults']['control_spec_id']]
        assert spec['type']==mode and spec['enabled']==(mode=='canny')
        assert spec['backend']['id']=='comfy-native-canny'
        assert spec['backend']['parameters']=={'low_threshold':.2,'high_threshold':.4}
        assert spec['strength']==.6 and spec['schedule']=={'start_percent':.1,'end_percent':.9}
        assert updated['defaults']==original['defaults'] and updated['reference_bindings']==original['reference_bindings']


@pytest.mark.parametrize('capture',[{}, [], None, {'schemas':{},'runtime':{}},
    {'schemas':{},'runtime':None}, {'schemas':{'Canny':None},'runtime':{'core_commit':'daeb5e53681e2b10a3f0727d9ec5bc90784bee10'}}])
def test_profile_helper_malformed_schema_is_typed_before_native_provider_access(tmp_path,capture):
    path=tmp_path/'bad-schema.json'
    path.write_text(json.dumps(capture),encoding='utf-8')
    with pytest.raises(ContractError,match='MODEL_INCOMPATIBLE') as error:
        h3_nodes.H3Profile().execute(str(tmp_path),str(path),'canny',
                                   **{k+'_file':v for k,v in h3_nodes.DEFAULT_FILES.items()})
    assert str(tmp_path) not in str(error.value)


def test_preparation_control_settings_need_no_h3_components_or_sampling_profile():
    data=project()
    record=Project.from_dict(data)
    policy=RenderProfile.from_dict(data['render_profiles'][data['defaults']['render_profile_id']])
    assert policy['components']=={} and policy['sampling']=={}
    configured=h3_nodes.ControlSettings().execute(record,policy,'canny',.4,.8,1.,0.,1.)['result'][0]
    assert configured['controls'][configured['defaults']['control_spec_id']]['backend']['id']=='comfy-native-canny'
    assert configured['render_profiles']==record['render_profiles']


def test_actual_owned_expander_wrapper_returns_native_links_expansion_and_honest_status(tmp_path,native_builder):
    # Pure source compiler with synthetic declared availability; no native
    # executor, loader, sampler, image tensor or checkpoint is called/accessed.
    w,p,models,control,prompt,ctx,_,parent=setup(tmp_path)
    data=project()
    data['windows']={w.id:w.to_dict()}
    data['render_profiles'][p['id']]=p.to_dict()
    spatial=data['spatial_transforms'][w['spatial_transform_id']]
    spatial.update(coded_width=32,coded_height=32,display_width=32,display_height=32,
        fitted_width=32,fitted_height=32,canvas_width=32,canvas_height=32,output_width=32,output_height=32)
    spatial['content_rect']={'x':0,'y':0,'width':32,'height':32}
    compiled=h3_nodes.ExpandNativeRender().execute(str(tmp_path),ctx.versions['native_schema_file'],'1073741824',
        Project.from_dict(data),w,p,control,prompt,models.model.as_list(),models.clip.as_list(),
        models.video_vae.as_list(),models.audio_vae.as_list(),parent,'synthetic-wrapper',patch=models.patch.as_list())
    assert compiled['ui']['h3_report'][0]['code']=='GRAPH_COMPILED'
    assert compiled['ui']['h3_report'][0]['gpu']=='not_performed'
    graph=compiled['expand']
    for link,kind in zip(compiled['result'][:3],('VAEDecode','VAEDecodeAudio','KVD_NativeReceipt')):
        assert graph[link[0]]['class_type']==kind and link[1]==0
