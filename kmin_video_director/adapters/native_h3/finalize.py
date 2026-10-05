"""Validate and persist exact useful decoded output; never attest sampling/GPU acceptance."""
from fractions import Fraction

from ...contracts import RenderResult, cache_key, cache_locator, digest_bytes, digest_json, stable_id
from ...contracts.worker import FinalizedWindow
from ...controls.storage import check_geometry
from ...errors import fail
from ...version import SCHEMA_VERSION
from .media_bridge import encode_rgb, write_json
from .order import DecodeReceipt, FinalizedToken

VERSION = 'kvd-useful-finalizer/1.0.0'


def validate_images(decoded,*,synthetic=False):
    n,w,h=decoded.frame_count,decoded.width,decoded.height
    images=decoded.images
    if synthetic and isinstance(images,(tuple,list)):
        if len(images)!=n or any(not isinstance(f,bytes) or len(f)!=w*h*3 for f in images):
            fail('FRAME_COUNT_MISMATCH','Synthetic decoded pixels must match exact N/H/W/3 geometry.')
    else:
        try:
            import torch
        except ImportError:
            fail('DEPENDENCY_MISSING','Native IMAGE finalization requires the existing Torch backend.')
        if not isinstance(images,torch.Tensor) or tuple(images.shape)!=(n,h,w,3) or not images.is_floating_point():
            fail('FRAME_COUNT_MISMATCH','Decoded native IMAGE must be float N/H/W/3 with the exact native count.')
        for image in images:
            if not bool(torch.isfinite(image).all()) or bool((image<0).any()) or bool((image>1).any()):
                fail('FRAME_COUNT_MISMATCH','Decoded IMAGE values must be finite in 0..1.')


def useful_frames(decoded,window,spatial,context,*,synthetic=False):
    rect=spatial['content_rect']
    width=decoded.width
    bounds=window['output_useful_range']
    for index in range(bounds['start'],bounds['end']):
        context.cancellation.check()
        frame=decoded.images[index]
        if not synthetic:
            import torch
            frame=frame.detach().to(device='cpu',dtype=torch.float32).mul(255).round().to(dtype=torch.uint8).contiguous().numpy().tobytes()
        yield b''.join(frame[((rect['y']+y)*width+rect['x'])*3:((rect['y']+y)*width+rect['x']+rect['width'])*3]
                       for y in range(rect['height']))


def finalize_window(decoded,window,snapshot,spatial,attempt,request_id,order_token,*,context):
    context.cancellation.check()
    s=check_geometry(spatial,window['inference_frame_count'])
    if type(attempt) is not int or attempt<1 or not isinstance(request_id,str) or not request_id.strip():
        fail('INVALID_RECORD','Finalization needs a positive attempt and explicit request ID.')
    project=snapshot.project
    if (project.id!=window['project_id'] or project['windows'].get(window.id)!=window.to_dict() or
        snapshot.settings.get(window['segment_id']) is None or
        snapshot.settings[window['segment_id']].to_dict()!=window['resolved_settings'] or
        project['spatial_transforms'].get(spatial.id)!=s or spatial.id!=window['spatial_transform_id']):
        fail('STALE_DEPENDENCY','Finalization requires the exact current resolved Project/window/spatial snapshot.')
    if decoded.frame_count!=window['inference_frame_count'] or (decoded.width,decoded.height)!=(s['canvas_width'],s['canvas_height']):
        fail('FRAME_COUNT_MISMATCH','Decoded native counts/geometry differ from the requested bounded window.')
    if not isinstance(order_token,DecodeReceipt) or order_token.origin not in ('native','synthetic_decoded'):
        fail('PARTIAL_RESULT','A decoded native execution receipt is required before finalization.')
    synthetic=order_token.origin=='synthetic_decoded'
    if synthetic and context.versions.get('evidence')!='synthetic_decoded':
        fail('INVALID_EVIDENCE','Synthetic decoded fixtures must be explicitly identified.')
    token=order_token.manifest
    expected={'window_id':window.id,'generation_key':window['generation_key'],'project_id':project.id,
        'plan_revision':window['plan_revision'],'ordinal':window['ordinal'],'requested_frames':decoded.frame_count,
        'width':decoded.width,'height':decoded.height,'prompt_digest':digest_bytes(window['compiled_prompt'].encode('utf-8')),
        'profile_digest':digest_json(project['render_profiles'][window['render_profile_id']])}
    if any(token.get(k)!=v for k,v in expected.items()) or not token.get('native_graph_digest'):
        fail('STALE_DEPENDENCY','The decoded receipt differs from the current generation key, prompt, profile or window.')
    validate_images(decoded,synthetic=synthetic)
    rect=s['content_rect']
    if s['output_sar']!={'num':1,'den':1} or s['output_width']!=s['display_width'] or s['output_height']!=s['display_height']:
        fail('UNSUPPORTED_EXPORT_DIMENSIONS','Final output must recover the declared square-pixel display geometry.')
    if window['resolved_settings']['spatial_policy']=='preserve_display_pad' and (rect['width'],rect['height'])!=(s['output_width'],s['output_height']):
        fail('UNSUPPORTED_EXPORT_DIMENSIONS','Preserve-display padding cannot silently resize content.')
    mode=window['resolved_settings']['audio_mode']
    if mode=='generate':
        fail('UNSUPPORTED_CAPABILITY','Generated PCM finalization awaits reviewed media global-sample integration; choose preserve or mute.')
    # Original PCM binding/origin remains Project-global and is consumed by media assembly.
    audio={'mode':mode,'source_offset':project['audio_timeline']['source_offset'],
           'policy':'project_global_pcm' if mode=='preserve' else 'mute','native_audio_retained':False}
    count=window['useful_range']['end']-window['useful_range']['start']
    # The actual graph receipt contains transport fields (map locator, selected
    # folder and native node IDs). Retain it as provenance, not cache identity.
    key=cache_key('generation',{'generation_key':window['generation_key'],'request_id':request_id,'attempt':attempt,
                          'spatial':s,'audio_policy':audio},algorithm_version=VERSION)
    locator=cache_locator('generation',key,suffix='nut')
    video=encode_rgb(useful_frames(decoded,window,s,context,synthetic=synthetic),locator['path'],count,
        rect['width'],rect['height'],context=context,output_width=s['output_width'],output_height=s['output_height'])
    # Local CPU probe is provisional until the separately reviewed media policy is integrated.
    coverage={'useful_range':window['useful_range'],'output_useful_range':window['output_useful_range'],
        'requested_frames':decoded.frame_count,'decoded_frames':decoded.frame_count,'useful_frames':count,
        'width':s['output_width'],'height':s['output_height'],'fps':{'num':24,'den':1},
        'padding_removed':True,'context_removed':True,'pts_digest':video['probe']['video']['pts_digest']}
    receipt={'version':VERSION,'evidence':'synthetic_decoded' if synthetic else 'native_decoded_cpu_finalization',
        'gpu':'not_performed','generation_key':window['generation_key'],'decoded_receipt':token,
        'spatial':s,'coverage':coverage,'audio':audio,'artifacts':[video.to_dict()]}
    receipt_locator=cache_locator('generation',key,suffix='json')
    write_json(receipt,receipt_locator['path'],context)
    result=RenderResult.from_dict({'kind':'kmin.render_result','schema_version':SCHEMA_VERSION,
        'id':stable_id('result',request_id,attempt,key),'required_features':[],'extensions':{},
        'request_id':request_id,'attempt':attempt,'project_id':project.id,'segment_id':window['segment_id'],
        'window_id':window.id,'generation_key':window['generation_key'],'status':'succeeded','stage':'trim',
        'progress':{'done':count,'total':count,'unit':'useful_frame'},'artifacts':[video.to_dict()],
        'coverage':coverage,'audio':audio,'provenance':{'version':VERSION,'receipt_digest':digest_json(receipt)},
        'validation':{'evidence_kind':'cpu_media','gpu':'not_performed','receipts':[receipt_locator['path']]},
        'error':None,'warnings':['Decoded-output CPU finalization does not attest H3/GPU or human-result acceptance.',
                                'Media global timing/assembly integration remains gated on its reviewed common SHA.']})
    context.cancellation.check()
    return FinalizedWindow(result,FinalizedToken(project.id,window['plan_revision'],window['ordinal'],
                                                window['useful_range']['end'],result.id,window['generation_key']))
