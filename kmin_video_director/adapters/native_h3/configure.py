"""Human-requested profile preparation from explicit filenames and header metadata."""
from pathlib import Path

from ...contracts import RenderProfile
from .checkpoints import read_header, architecture_metadata
from .profile import VERSION, CORES, enum_value, incompatible, schema_digest, validate_native_profile
from .components import REVISION, DEFAULT_FILES, COMPONENTS
from .schema import read_handoff


def configure_profile(files,structural,*,context):
    context.cancellation.check()
    schemas, core = read_handoff(context)
    if core not in CORES: incompatible('This exact core has no checked source adapter.')
    roles=('model','clip','video_vae','audio_vae')+(('patch',) if structural else ())
    providers={'model':('UNETLoader','unet_name','diffusion_models'),
        'clip':('CLIPLoader','clip_name','text_encoders'),'video_vae':('VAELoader','vae_name','vae'),
        'audio_vae':('VAELoader','vae_name','vae'),'patch':('ModelPatchLoader','name','model_patches')}
    # Dropdown availability is a resource check, before any selected-file read.
    for role in roles:
        if Path(files[role]).name!=DEFAULT_FILES[role]:
            incompatible('This initial profile pins the source template filenames; alternative checkpoints need a reviewed profile.')
        enum_value(schemas,*providers[role][:2],files[role])
    try:
        import folder_paths
    except ImportError:
        from ...errors import fail
        fail('DEPENDENCY_MISSING','Human profile preparation requires the existing native model path provider.')
    components={}
    for role in roles:
        context.cancellation.check()
        path=folder_paths.get_full_path(providers[role][2],files[role])
        if not path: incompatible(f'The explicitly selected checkpoint is absent: {role}.')
        header,fp=read_header(path,context=context)
        if fp['digest']['hex']!=COMPONENTS[role][1] or fp['byte_size']!=COMPONENTS[role][2]:
            incompatible(f'Selected {role} content differs from the pinned public model revision.')
        components[role]={'filename':files[role],'revision':REVISION,'digest':fp['digest'],
                          'format':'comfy-native','metadata':architecture_metadata(header,role)}
    branch={}
    if structural:
        patch=components['patch']['metadata']
        if patch['hidden_size']!=components['model']['metadata']['hidden_size']:
            incompatible('Control/base hidden widths differ.')
        branch={'version':'union-v1' if patch['block_count']==5 else 'union-v2',
                **{key:patch[key] for key in ('block_count','injection_layers','input_channels','adaln','normalization_mode')}}
    p=RenderProfile.from_dict({'id':'h3-native-initial','version':VERSION,'evidence':'source_only','receipts':[],
        'fps':{'num':24,'den':1},'lattice':{'offset':5,'step':17},'shape_min':5,
        'policy_inference_min':124,'policy_inference_max':345,'policy_duration_max':{'num':15,'den':1},
        'grid':32,'base_family':'ref2va','components':components,'node_signatures':{k:schema_digest(v) for k,v in schemas.items()},
        'core_revision':core,'runtime':{'metadata_evidence':'selected header and complete file SHA256; native load/GPU NOT PERFORMED',
                                      'component_revision_policy':'content SHA256 and size matched pinned public LFS metadata'},
        'sampling':{'sampler_name':'res_multistep','scheduler':'simple','steps':20,'denoise':1.0,'shift_video':12.,'shift_audio':3.},
        'control_branch':branch,'memory_policy':'one_window'})
    return validate_native_profile(p,schemas,core,structural=structural)
