"""Native GraphBuilder expansion; no sampling, loading or HTTP self-queue here."""
import json
import math

from ...contracts import ControlSpec, Settings, digest_bytes, digest_json, require_runtime_capabilities
from ...contracts.worker import ExpandedRender, NativeLink
from ...errors import fail
from ...controls.storage import check_count
from .profile import VERSION, enum_options, enum_value, incompatible, native_digest, port_type, validate_native_profile
from .schema import read_handoff

# These are executable helper nodes in owned h3_nodes.py, not protocol classes.
OWN_SCHEMAS = {
    'KVD_WindowGate': ({'project_id':'STRING','plan_revision':'INT','ordinal':'INT',
                        'useful_start':'INT'}, {'order_token':'KVD_ORDER'}, ('KVD_GATE',)),
    'KVD_OrderedModel': ({'model':'MODEL','gate':'KVD_GATE'}, {}, ('MODEL',)),
    'KVD_OrderedClip': ({'clip':'CLIP','gate':'KVD_GATE'}, {}, ('CLIP',)),
    'KVD_ControlImage': ({'manifest':'STRING','asset_root':'STRING','working_set_bytes':'STRING','gate':'KVD_GATE'}, {}, ('IMAGE',)),
    'KVD_NativeReceipt': ({'images':'IMAGE','audio':'AUDIO','manifest':'STRING','gate':'KVD_GATE'}, {}, ('KVD_ORDER',)),
    'KVD_FinalizeWindow': ({}, {}, ('KVD_RENDER_RESULT','KVD_ORDER','KVD_PROJECT','STRING')),
}


def generation_key(window, profile, control, prompt, spec):
    """Bind the plan, exact text, maps, sampling, model and native schema revisions."""
    return digest_json({'adapter':VERSION,'window':{k:window[k] for k in
        ('id','project_id','segment_id','ordinal','plan_revision','useful_range','input_spans',
         'inference_frame_count','output_useful_range','context','padding','spatial_transform_id',
         'resolved_settings_digest','plan_digest')},
        'profile':profile.to_dict(),'control':spec.to_dict(),
        'map':{'fingerprint':{k:control.media['fingerprint'][k] for k in
                ('digest','byte_size','video_stream','audio_stream','probe_version','decoder_version')},
               'probe':control.media['probe'], 'role':control.media['role'], 'spatial_transform_id':control.spatial_transform_id,
               'frame_count':control.frame_count} if control.media else None,'prompt':prompt.digest})


def own_schema(cls):
    required,optional,outputs = OWN_SCHEMAS[cls]
    return {'input':{'required':{k:[v,{}] for k,v in required.items()},
                     'optional':{k:[v,{}] for k,v in optional.items()}},'output':list(outputs)}


def verify_graph(graph, schemas, parent):
    """Verify actual class, required port, enum/scalar and link-slot/type contracts."""
    all_nodes = {**parent,**graph}
    for node in graph.values():
        cls = node['class_type']
        schema = own_schema(cls) if cls in OWN_SCHEMAS else schemas.get(cls)
        if not schema:
            incompatible(f'Native class is unavailable: {cls}.')
        inputs = node['inputs']
        required = schema['input'].get('required',{})
        ports = {**required,**schema['input'].get('optional',{})}
        if not set(required) <= set(inputs) or not set(inputs) <= set(ports):
            incompatible(f'Invalid required/optional native ports: {cls}.')
        for key,value in inputs.items():
            kind = port_type(ports[key])
            link = isinstance(value,list) and len(value) == 2 and isinstance(value[0],str) and type(value[1]) is int
            if link:
                origin = all_nodes.get(value[0],{})
                source_cls = origin.get('class_type')
                source_schema = own_schema(source_cls) if source_cls in OWN_SCHEMAS else schemas.get(source_cls,{})
                outputs = source_schema.get('output',[])
                if not 0 <= value[1] < len(outputs) or outputs[value[1]] != kind:
                    incompatible(f'Wrong native source slot/type for {cls}.{key}.')
            elif kind == 'COMBO':
                if value not in enum_options(ports[key]): incompatible(f'Unsupported native enum: {cls}.{key}.')
            elif (kind == 'INT' and type(value) is not int or
                  kind == 'FLOAT' and type(value) not in (int,float) or
                  kind == 'FLOAT' and not math.isfinite(value) or
                  kind == 'BOOLEAN' and type(value) is not bool or
                  kind == 'STRING' and not isinstance(value,str) or
                  kind not in ('INT','FLOAT','STRING','BOOLEAN','COMBO')):
                incompatible(f'Wrong literal/native link: {cls}.{key}.')
            if not link and len(ports[key]) > 1:
                options = ports[key][1]
                if kind in ('INT','FLOAT') and (value < options.get('min',value) or value > options.get('max',value)):
                    incompatible(f'Native widget range exceeded: {cls}.{key}.')


def _check_models(models, profile, schemas, parent, structural):
    for role,cls,port,kind in (('model','UNETLoader','unet_name','MODEL'),
        ('clip','CLIPLoader','clip_name','CLIP'),('video_vae','VAELoader','vae_name','VAE'),
        ('audio_vae','VAELoader','vae_name','VAE'),('patch','ModelPatchLoader','name','MODEL_PATCH')):
        if role == 'patch' and not structural: continue
        link = getattr(models,role)
        if link is None: incompatible('Select the verified native control checkpoint.')
        node = parent.get(link.node_id,{})
        if node.get('class_type') != cls or link.output_index != 0:
            incompatible(f'{role} must link the checked native loader output slot.')
        if node.get('inputs',{}).get(port) != profile['components'][role]['filename']:
            incompatible(f'{role} loader filename differs from the checked profile.')
        if role == 'clip' and node['inputs'].get('type') != 'minimax':
            incompatible('CLIPLoader must use its native minimax encoder type.')
        if role == 'model' and node['inputs'].get('weight_dtype') != 'default':
            incompatible('The first source profile uses the native default checkpoint dtype.')
        if role == 'clip' and node['inputs'].get('device','default') != 'default':
            incompatible('The first source profile retains native default text-encoder device management.')
        enum_value(schemas,cls,port,profile['components'][role]['filename'])


def expand_native_render(window, profile, models, control, prompt, order_token, *, context):
    context.cancellation.check()
    require_runtime_capabilities(window=window,settings=Settings.from_dict(window['resolved_settings']))
    if window['reference_manifest']:
        fail('UNSUPPORTED_CAPABILITY','The first native path requires empty reference inputs.')
    check_count(window['inference_frame_count'])
    schemas, core = read_handoff(context)
    try:
        parent = json.loads(context.versions['source_graph'])
        spec = ControlSpec.from_dict(json.loads(context.versions['control_spec_json']))
        width,height = int(context.versions['canvas_width']),int(context.versions['canvas_height'])
        owner = context.versions['native_node_id']
        if (not isinstance(parent, dict) or not isinstance(owner, str) or not owner or
            any(not isinstance(v, dict) or not isinstance(v.get('inputs'), dict) for v in parent.values())):
            raise ValueError
    except (KeyError,ValueError,OSError,TypeError):
        incompatible('Supply the explicit native schema handoff, source graph, canvas and control spec.')
    structural = spec['enabled'] and spec['type'] == 'canny'
    validate_native_profile(profile,schemas,core,structural=structural)
    if window['render_profile_id'] != profile['id'] or profile['id'] not in spec['compatibility']['profile_ids']:
        incompatible('Window/control profile IDs differ.')
    if (control.window_id != window.id or control.control_spec_id != window['control_spec_id'] or
        spec.id != control.control_spec_id or control.spatial_transform_id != window['spatial_transform_id'] or
        control.frame_count != window['inference_frame_count'] or structural != (control.media is not None)):
        incompatible('Control artifact does not match this exact bounded window.')
    if width <= 0 or height <= 0 or width%32 or height%32:
        incompatible('Native canvas must use the profile 32-pixel grid.')
    if control.media:
        video = control.media['probe']['video']
        if not video or (video['width'],video['height']) != (width,height) or video['rate'] != {'num':24,'den':1}:
            incompatible('Structural control must match exact N/H/W/3 IMAGE geometry at 24 FPS.')
        if spec['map_fingerprint'] is not None and spec['map_fingerprint'] != control.media['fingerprint']['digest']:
            incompatible('Control map bytes differ from the explicitly declared map fingerprint.')
    if prompt.text != window['compiled_prompt'] or prompt.digest != digest_bytes(prompt.text.encode('utf-8')) or prompt.reference_manifest:
        fail('PROMPT_INVALID','Native text must be the exact authored, digested no-reference window text.')
    if generation_key(window,profile,control,prompt,spec) != window['generation_key']:
        fail('STALE_DEPENDENCY','Bind the current prompt, control, plan, model and sampling generation key.')
    if window['ordinal'] > 0 and order_token is None or window['ordinal'] == 0 and order_token is not None:
        incompatible('Serial windows require the predecessor finalization token, with no token for the first window.')
    _check_models(models,profile,schemas,parent,structural)
    context.cancellation.check()
    try:
        from comfy_execution.graph_utils import GraphBuilder
    except ImportError:
        fail('DEPENDENCY_MISSING','Native Comfy GraphBuilder is required; no substitute execution backend.',stage='prepare')
    # Explicit per-owner/window prefix is deterministic and independent of sampler settings.
    prefix = 'kvd.'+digest_bytes((owner+'\0'+window.id).encode())['hex'][:24]+'.'
    graph = GraphBuilder(prefix=prefix)
    gate_inputs = {'project_id':window['project_id'],'plan_revision':window['plan_revision'],
                   'ordinal':window['ordinal'],'useful_start':window['useful_range']['start']}
    if order_token: gate_inputs['order_token'] = order_token.as_list()
    gate = graph.node('KVD_WindowGate',id='gate',**gate_inputs)
    model = graph.node('KVD_OrderedModel',id='model',model=models.model.as_list(),gate=gate.out(0))
    clip = graph.node('KVD_OrderedClip',id='clip',clip=models.clip.as_list(),gate=gate.out(0))
    sampling = profile['sampling']
    shifted = graph.node('MiniMaxH3SigmaShift',id='shift',model=model.out(0),
                         shift_video=sampling['shift_video'],shift_audio=sampling['shift_audio'])
    sampled_model = shifted.out(0)
    if structural:
        manifest = json.dumps(control.media.to_dict(),ensure_ascii=False,sort_keys=True,separators=(',',':'))
        image = graph.node('KVD_ControlImage',id='map',manifest=manifest,asset_root=str(context.asset_root),
            working_set_bytes=context.versions.get('working_set_bytes','1073741824'),gate=gate.out(0))
        patch = graph.node('MiniMaxH3FunControlNetApply',id='patch',model=sampled_model,
            model_patch=models.patch.as_list(),vae=models.video_vae.as_list(),strength=spec['strength'],
            start_percent=spec['schedule']['start_percent'],end_percent=spec['schedule']['end_percent'],control_video=image.out(0))
        sampled_model = patch.out(0)
    condition = graph.node('MiniMaxH3ReferenceToVideo',id='condition',clip=clip.out(0),
        prompt=prompt.text,width=width,height=height,length=window['inference_frame_count'],ref_image_size='match')
    guider = graph.node('BasicGuider',id='guider',model=sampled_model,conditioning=condition.out(0))
    sigmas = graph.node('BasicScheduler',id='sigmas',model=sampled_model,scheduler=sampling['scheduler'],
                        steps=sampling['steps'],denoise=sampling['denoise'])
    noise = graph.node('RandomNoise',id='noise',noise_seed=int(window['resolved_settings']['seed']))
    sampler = graph.node('KSamplerSelect',id='sampler',sampler_name=sampling['sampler_name'])
    latent = graph.node('SamplerCustomAdvanced',id='sample',noise=noise.out(0),guider=guider.out(0),
        sampler=sampler.out(0),sigmas=sigmas.out(0),latent_image=condition.out(1))
    images = graph.node('VAEDecode',id='decode',samples=latent.out(1),vae=models.video_vae.as_list())
    audio = graph.node('VAEDecodeAudio',id='decode-audio',samples=latent.out(1),vae=models.audio_vae.as_list())
    body = graph.finalize()
    receipt = {'version':VERSION,'window_id':window.id,'generation_key':window['generation_key'],
        'project_id':window['project_id'],'plan_revision':window['plan_revision'],'ordinal':window['ordinal'],
        'useful_range':window['useful_range'],'requested_frames':window['inference_frame_count'],
        'width':width,'height':height,'prompt_digest':prompt.digest,'profile_digest':digest_json(profile),
        'native_graph_digest':native_digest(body),'gpu':'not_performed'}
    token = graph.node('KVD_NativeReceipt',id='receipt',images=images.out(0),audio=audio.out(0),
                       gate=gate.out(0),manifest=json.dumps(receipt,sort_keys=True,separators=(',',':')))
    body = graph.finalize()
    verify_graph(body,schemas,parent)
    context.cancellation.check()
    return ExpandedRender(body,NativeLink(images.id,0),NativeLink(audio.id,0),NativeLink(token.id,0),native_digest(body))
