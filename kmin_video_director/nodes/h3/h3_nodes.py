"""Real import-safe operations. No optional imports or model reads in INPUT_TYPES."""
import json
from pathlib import Path

from ...contracts import (GenerationWindow, Project, Settings, MediaRef, ControlSpec, RenderProfile,
                         dumps, digest_json, resolve_project)
from ...contracts.worker import OperationContext, NativeLink, NativeModelLinks, DecodedAV
from ...registration import build_registry
from ...errors import fail
from ...controls.canny import build_control, thresholds, VERSION as CANNY_VERSION
from ...controls.storage import raw_frames
from ...adapters.native_h3.prompt import compile_window_prompt
from ...adapters.native_h3.graph import expand_native_render, generation_key
from ...adapters.native_h3.finalize import finalize_window, validate_images, collect_result
from ...adapters.native_h3.configure import configure_profile, DEFAULT_FILES
from ...adapters.native_h3.profile import CORES
from ...adapters.native_h3.order import DecodeReceipt, check_predecessor


class NativeCancellation:
    def check(self):
        try:
            from comfy.model_management import throw_exception_if_processing_interrupted
        except ImportError:
            return  # Pure CPU call environments use their explicit operation context.
        throw_exception_if_processing_interrupted()


def context_for(project_root,**versions):
    if not str(project_root).strip(): fail('INVALID_LOCATOR','Select your existing local project folder.')
    root=Path(project_root)
    if not root.is_dir(): fail('INVALID_LOCATOR','The explicitly selected project folder must already exist.')
    return OperationContext(root,NativeCancellation(),{k:str(v) for k,v in versions.items()})


def io_fields():
    return {'project_root':('STRING',{'default':''}), 'ffmpeg_path':('STRING',{'default':''}),
        'ffprobe_path':('STRING',{'default':''}), 'disk_quota_bytes':('STRING',{'default':str(4*1024**3)}),
        'working_set_bytes':('STRING',{'default':'268435456'}),'timeout_seconds':('STRING',{'default':'1200'})}


def dispatch(name,*args,**kwargs):
    return build_registry().require_operation(name)(*args,**kwargs)


def output(values,code,**data):
    return {'result':tuple(values),'ui':{'h3_report':[{'code':code,'gpu':'not_performed',**data}]}}


class H3Profile:
    CATEGORY='KVD/H3'
    FUNCTION='execute'
    RETURN_TYPES=('KVD_RENDER_PROFILE','STRING')
    RETURN_NAMES=('render_profile','profile_report')
    DESCRIPTION='Check explicit source-template filename availability and safetensors metadata. Does not load models or establish GPU fit.'
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'project_root':('STRING',{'default':''}),'native_schema_file':('STRING',{'default':''}),
            'structural_control':(['canny','off'],),**{role+'_file':('STRING',{'default':name}) for role,name in DEFAULT_FILES.items()}}}
    @classmethod
    def IS_CHANGED(cls,**kwargs): return float('nan')
    def execute(self,project_root,native_schema_file,structural_control,**files):
        profile=configure_profile({k:files[k+'_file'] for k in DEFAULT_FILES},structural_control=='canny',
            context=context_for(project_root,native_schema_file=native_schema_file))
        return output((profile,json.dumps(profile.to_dict(),ensure_ascii=False)),'PROFILE_SOURCE_CHECKED')


class BuildControl:
    CATEGORY='KVD/H3'
    FUNCTION='execute'
    RETURN_TYPES=('KVD_CONTROL','STRING')
    RETURN_NAMES=('control','control_report')
    DESCRIPTION='Build exact native Canny maps from one prepared disk window, or explicitly remove structural control.'
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{**io_fields(),'prepared':('KVD_PREPARED',),'project':('KVD_PROJECT',)}}
    @classmethod
    def IS_CHANGED(cls,**kwargs): return float('nan')
    def execute(self,prepared,project,**io):
        w=project['windows'].get(prepared.window_id)
        if not w: fail('STALE_DEPENDENCY','Prepared window is absent from this Project.')
        spec=ControlSpec.from_dict(project['controls'][w['control_spec_id']])
        control=dispatch('BuildControl',prepared,spec,context=context_for(**io))
        report={'code':'CONTROL_READY' if control.media else 'CONTROL_OFF','frames':control.frame_count,
                'map_digest':control.media['fingerprint']['digest'] if control.media else None,'gpu':'not_performed'}
        return output((control,json.dumps(report)),report['code'],**{k:v for k,v in report.items() if k!='code'})


class ControlSettings:
    CATEGORY='KVD/H3'
    FUNCTION='execute'
    RETURN_TYPES=('KVD_PROJECT',)
    RETURN_NAMES=('project',)
    DESCRIPTION='Choose native Canny or structural off before planning. Preparation uses a source-only shape policy and needs no H3 weights; generation has a separate strict profile preflight.'
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'project':('KVD_PROJECT',),'render_profile':('KVD_RENDER_PROFILE',),'control_mode':(['canny','off'],),
            'low_threshold':('FLOAT',{'default':.4,'min':.01,'max':.99,'step':.01}),
            'high_threshold':('FLOAT',{'default':.8,'min':.01,'max':.99,'step':.01}),
            'strength':('FLOAT',{'default':1.,'min':0.,'max':1.}),
            'start_percent':('FLOAT',{'default':0.,'min':0.,'max':1.}),
            'end_percent':('FLOAT',{'default':1.,'min':0.,'max':1.})}}
    def execute(self,project,render_profile,control_mode,low_threshold,high_threshold,strength,start_percent,end_percent):
        if project['windows']: fail('STALE_DEPENDENCY','Configure structural control on the unplanned Project, then replan.')
        if control_mode not in ('canny','off'): fail('UNSUPPORTED_CAPABILITY','Choose Canny or explicit off.')
        thresholds(low_threshold,high_threshold)
        if (render_profile['id']!=project['defaults']['render_profile_id'] or
            project['render_profiles'].get(render_profile['id'])!=render_profile.to_dict()):
            fail('STALE_DEPENDENCY','Create the media Project using this exact H3 profile.')
        if render_profile['core_revision'] not in CORES:
            fail('MODEL_INCOMPATIBLE','Preparation requires a checked native Canny source/shape policy.')
        # Extraction needs the shape policy, not H3 checkpoint metadata. The
        # separate H3 profile/expander checks all generation resources strictly.
        p=project.to_dict()
        spec=p['controls'][p['defaults']['control_spec_id']]
        spec.update(type=control_mode,enabled=control_mode=='canny',strength=strength,
                    schedule={'start_percent':start_percent,'end_percent':end_percent},preprocess_version=CANNY_VERSION,map_fingerprint=None)
        spec['backend'].update(id='comfy-native-canny',version='source-daeb5e5' if render_profile['core_revision'].startswith('daeb5e5') else 'source-b87fe48',
                              parameters={'low_threshold':low_threshold,'high_threshold':high_threshold},model_digest=None,temporal_policy='fixed_parameters')
        spec['compatibility']={'profile_ids':[render_profile['id']],'evidence':'source_only'}
        p['controls'][spec['id']]=ControlSpec.from_dict(spec).to_dict()
        p['revision']+=1
        return output((Project.from_dict(p),),'CONTROL_CONFIGURED')


class CompileWindowPrompt:
    CATEGORY='KVD/H3'
    FUNCTION='execute'
    RETURN_TYPES=('KVD_WINDOW','KVD_PROMPT','STRING')
    RETURN_NAMES=('window','compiled_prompt','prompt_text')
    DESCRIPTION='Use the visible authored text for this selected window. No hidden enhancer, references or rewrite.'
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'window':('KVD_WINDOW',),'prompt':('STRING',{'default':'','multiline':True})}}
    def execute(self,window,prompt):
        data=window.to_dict()
        data['compiled_prompt']=prompt
        window=GenerationWindow.from_dict(data)
        ctx=OperationContext(Path('.'),NativeCancellation(),{})  # This operation never reads files.
        compiled=dispatch('CompileWindowPrompt',window,Settings.from_dict(window['resolved_settings']),(),context=ctx)
        return output((window,compiled,compiled.text),'PROMPT_AUTHORED',prompt_digest=compiled.digest)


class BindWindow:
    CATEGORY='KVD/H3'
    FUNCTION='execute'
    RETURN_TYPES=('KVD_PROJECT','KVD_WINDOW')
    RETURN_NAMES=('project','window')
    DESCRIPTION='Freeze the actual prompt, map, profile and sampling generation key in the selected Project window.'
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'project':('KVD_PROJECT',),'window':('KVD_WINDOW',),'render_profile':('KVD_RENDER_PROFILE',),
                            'control':('KVD_CONTROL',),'compiled_prompt':('KVD_PROMPT',)}}
    def execute(self,project,window,render_profile,control,compiled_prompt):
        if project['windows'].get(window.id) is None or project['render_profiles'].get(render_profile['id'])!=render_profile.to_dict():
            fail('STALE_DEPENDENCY','Replan using the selected profile before binding this window.')
        spec=ControlSpec.from_dict(project['controls'][window['control_spec_id']])
        data=window.to_dict()
        data['generation_key']=generation_key(window,render_profile,control,compiled_prompt,spec)
        window=GenerationWindow.from_dict(data)
        p=project.to_dict()
        if p['windows'][window.id]!=data:
            p['windows'][window.id]=data
            p['active_result_by_window'].pop(window.id,None)
            p['revision']+=1
        return output((Project.from_dict(p),window),'WINDOW_BOUND',generation_key=data['generation_key'])


class ExpandNativeRender:
    CATEGORY='KVD/H3'
    FUNCTION='execute'
    RETURN_TYPES=('IMAGE','AUDIO','KVD_ORDER','STRING')
    RETURN_NAMES=('images','audio','order_token','graph_report')
    DESCRIPTION='Expand native conditioning, sampling and decoding in the current native queue; no recursive self-queue or hidden sampler.'
    @classmethod
    def INPUT_TYPES(cls):
        raw=lambda kind:(kind,{'rawLink':True})
        return {'required':{'project_root':('STRING',{'default':''}),'native_schema_file':('STRING',{'default':''}),
            'working_set_bytes':('STRING',{'default':'1073741824'}),
            'project':('KVD_PROJECT',),'window':('KVD_WINDOW',),'render_profile':('KVD_RENDER_PROFILE',),
            'control':('KVD_CONTROL',),'compiled_prompt':('KVD_PROMPT',),
            'model':raw('MODEL'),'clip':raw('CLIP'),'video_vae':raw('VAE'),'audio_vae':raw('VAE')},
            'optional':{'patch':raw('MODEL_PATCH'),'order_token':raw('KVD_ORDER')},
            'hidden':{'source_graph':'PROMPT','unique_id':'UNIQUE_ID'}}
    def execute(self,project_root,native_schema_file,working_set_bytes,project,window,render_profile,control,compiled_prompt,
                model,clip,video_vae,audio_vae,source_graph,unique_id,patch=None,order_token=None):
        spatial=project['spatial_transforms'][window['spatial_transform_id']]
        spec=project['controls'][window['control_spec_id']]
        link=lambda value:NativeLink(str(value[0]),int(value[1]))
        models=NativeModelLinks(link(model),link(clip),link(video_vae),link(audio_vae),link(patch) if patch else None)
        ctx=context_for(project_root,native_schema_file=native_schema_file,source_graph=json.dumps(source_graph),
            native_node_id=unique_id,control_spec_json=json.dumps(spec),canvas_width=spatial['canvas_width'],
            canvas_height=spatial['canvas_height'],working_set_bytes=working_set_bytes)
        expanded=dispatch('ExpandNativeRender',window,render_profile,models,control,compiled_prompt,link(order_token) if order_token else None,context=ctx)
        return {'result':(expanded.images.as_list(),expanded.audio.as_list(),expanded.order_token.as_list(),
                          json.dumps({'graph_digest':expanded.graph_digest,'evidence':'source_schema','gpu':'not_performed'})),
                'ui':{'h3_report':[{'code':'GRAPH_COMPILED','graph_digest':expanded.graph_digest,'gpu':'not_performed'}]},
                'expand':dict(expanded.graph)}


class FinalizeWindow:
    CATEGORY='KVD/H3'
    FUNCTION='execute'
    RETURN_TYPES=('KVD_RENDER_RESULT','KVD_ORDER','KVD_PROJECT','STRING')
    RETURN_NAMES=('render_result','order_token','project','result_json')
    OUTPUT_NODE=True
    DESCRIPTION='Persist exact useful video/PCM and collect current validated results as a JSON array for Select Results. Original sound keeps its global timeline; GPU acceptance is separate.'
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{**io_fields(),'images':('IMAGE',),'project':('KVD_PROJECT',),'window':('KVD_WINDOW',),
            'spatial':('KVD_SPATIAL',),'order_token':('KVD_ORDER',),'attempt':('INT',{'default':1,'min':1}),
            'request_id':('STRING',{'default':'manual-short-v2v'})},'optional':{'audio':('AUDIO',)}}
    @classmethod
    def IS_CHANGED(cls,**kwargs): return float('nan')
    def execute(self,images,project,window,spatial,order_token,attempt,request_id,audio=None,**io):
        shape=tuple(images.shape)
        if len(shape)!=4: fail('FRAME_COUNT_MISMATCH','Native decoded IMAGE must be N/H/W/3.')
        decoded=DecodedAV(images,audio,shape[0],shape[2],shape[1])
        finalized=dispatch('FinalizeWindow',decoded,window,resolve_project(project),spatial,attempt,request_id,order_token,context=context_for(**io))
        collected,results_json=collect_result(project,finalized.result)
        return output((finalized.result,finalized.order_token,collected,results_json),
                      'USEFUL_FINALIZED',**finalized.result['coverage'])


class WindowGate:
    CATEGORY='KVD/H3/Native helpers'
    FUNCTION='execute'
    RETURN_TYPES=('KVD_GATE',)
    RETURN_NAMES=('gate',)
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'project_id':('STRING',),'plan_revision':('INT',),'ordinal':('INT',),'useful_start':('INT',)},
                'optional':{'order_token':('KVD_ORDER',)}}
    def execute(self,project_id,plan_revision,ordinal,useful_start,order_token=None):
        NativeCancellation().check()
        return (check_predecessor(order_token,project_id=project_id,plan_revision=plan_revision,ordinal=ordinal,useful_start=useful_start),)


class OrderedModel:
    CATEGORY='KVD/H3/Native helpers'
    FUNCTION='execute'
    RETURN_TYPES=('MODEL',)
    RETURN_NAMES=('model',)
    @classmethod
    def INPUT_TYPES(cls): return {'required':{'model':('MODEL',),'gate':('KVD_GATE',)}}
    def execute(self,model,gate): NativeCancellation().check(); return (model,)


class OrderedClip:
    CATEGORY='KVD/H3/Native helpers'
    FUNCTION='execute'
    RETURN_TYPES=('CLIP',)
    RETURN_NAMES=('clip',)
    @classmethod
    def INPUT_TYPES(cls): return {'required':{'clip':('CLIP',),'gate':('KVD_GATE',)}}
    def execute(self,clip,gate): NativeCancellation().check(); return (clip,)


class ControlImage:
    CATEGORY='KVD/H3/Native helpers'
    FUNCTION='execute'
    RETURN_TYPES=('IMAGE',)
    RETURN_NAMES=('images',)
    @classmethod
    def INPUT_TYPES(cls): return {'required':{'manifest':('STRING',),'asset_root':('STRING',),'working_set_bytes':('STRING',),'gate':('KVD_GATE',)}}
    def execute(self,manifest,asset_root,working_set_bytes,gate):
        from ...adapters.native_h3.tensors import control_tensor
        return (control_tensor(MediaRef.from_dict(json.loads(manifest)),context=context_for(asset_root,working_set_bytes=working_set_bytes)),)


class ControlPreview:
    CATEGORY='KVD/H3'
    FUNCTION='execute'
    RETURN_TYPES=('IMAGE',)
    RETURN_NAMES=('preview',)
    DESCRIPTION='Show one real frame from the computed Canny map. Off has no structural preview.'
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'control':('KVD_CONTROL',),'project_root':('STRING',{'default':''}),
                            'preview_frame':('INT',{'default':0,'min':0,'max':344})}}
    def execute(self,control,project_root,preview_frame):
        if control.media is None: fail('UNSUPPORTED_CAPABILITY','Structural off has no Canny map to preview.')
        from ...adapters.native_h3.tensors import control_tensor
        return (control_tensor(control.media,context=context_for(project_root),preview_frame=preview_frame),)


class NativeReceipt:
    CATEGORY='KVD/H3/Native helpers'
    FUNCTION='execute'
    RETURN_TYPES=('KVD_ORDER',)
    RETURN_NAMES=('order_token',)
    @classmethod
    def INPUT_TYPES(cls): return {'required':{'images':('IMAGE',),'audio':('AUDIO',),'manifest':('STRING',),'gate':('KVD_GATE',)}}
    def execute(self,images,audio,manifest,gate):
        NativeCancellation().check()
        value=json.loads(manifest)
        validate_images(DecodedAV(images,audio,value['requested_frames'],value['width'],value['height']))
        return (DecodeReceipt(value,'native'),)


NODE_CLASS_MAPPINGS={'KVD_H3Profile':H3Profile,'KVD_BuildControl':BuildControl,
    'KVD_ControlSettings':ControlSettings,
    'KVD_CompileWindowPrompt':CompileWindowPrompt,'KVD_BindWindow':BindWindow,'KVD_ExpandNativeRender':ExpandNativeRender,
    'KVD_FinalizeWindow':FinalizeWindow,'KVD_WindowGate':WindowGate,'KVD_OrderedModel':OrderedModel,
    'KVD_OrderedClip':OrderedClip,'KVD_ControlImage':ControlImage,'KVD_NativeReceipt':NativeReceipt,'KVD_ControlPreview':ControlPreview}
NODE_DISPLAY_NAME_MAPPINGS={'KVD_H3Profile':'KVD H3 Profile','KVD_BuildControl':'KVD Canny Control',
    'KVD_ControlSettings':'KVD Structural Settings',
    'KVD_CompileWindowPrompt':'KVD Window Prompt','KVD_BindWindow':'KVD Bind Window',
    'KVD_ExpandNativeRender':'KVD Native H3 Render','KVD_FinalizeWindow':'KVD Finalize Window',
    'KVD_ControlPreview':'KVD Control Preview','KVD_WindowGate':'KVD Window Gate',
    'KVD_OrderedModel':'KVD Ordered Model','KVD_OrderedClip':'KVD Ordered CLIP',
    'KVD_ControlImage':'KVD Control IMAGE','KVD_NativeReceipt':'KVD Decode Receipt'}
OPERATIONS={'BuildControl':build_control,'CompileWindowPrompt':compile_window_prompt,
            'ExpandNativeRender':expand_native_render,'FinalizeWindow':finalize_window}
