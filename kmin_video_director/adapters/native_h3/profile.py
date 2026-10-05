"""Strict source/schema and explicitly recorded checkpoint compatibility checks.

These checks do not load weights, certify GPU fit, or attest inference.
"""
import math
import json
from pathlib import Path

from ...contracts import digest_bytes
from ...errors import fail
from .components import COMPONENTS, REVISION

CORES = frozenset(('b87fe48b0491425f682f7ffdaed56d0387cb6c5d',
                  'daeb5e53681e2b10a3f0727d9ec5bc90784bee10'))
VERSION = 'kvd-native-h3/1.0.0'
NATIVE_PORTS = {
    'UNETLoader': ({'unet_name':'COMBO','weight_dtype':'COMBO'}, ('MODEL',)),
    'CLIPLoader': ({'clip_name':'COMBO','type':'COMBO'}, ('CLIP',)),
    'VAELoader': ({'vae_name':'COMBO'}, ('VAE',)),
    'ModelPatchLoader': ({'name':'COMBO'}, ('MODEL_PATCH',)),
    'MiniMaxH3ReferenceToVideo': ({'clip':'CLIP','prompt':'STRING','width':'INT',
        'height':'INT','length':'INT','ref_image_size':'COMBO'}, ('CONDITIONING','LATENT')),
    'MiniMaxH3SigmaShift': ({'model':'MODEL','shift_video':'FLOAT','shift_audio':'FLOAT'}, ('MODEL',)),
    'MiniMaxH3FunControlNetApply': ({'model':'MODEL','model_patch':'MODEL_PATCH','vae':'VAE',
        'strength':'FLOAT','start_percent':'FLOAT','end_percent':'FLOAT'}, ('MODEL',)),
    'BasicGuider': ({'model':'MODEL','conditioning':'CONDITIONING'}, ('GUIDER',)),
    'BasicScheduler': ({'model':'MODEL','scheduler':'COMBO','steps':'INT','denoise':'FLOAT'}, ('SIGMAS',)),
    'RandomNoise': ({'noise_seed':'INT'}, ('NOISE',)),
    'KSamplerSelect': ({'sampler_name':'COMBO'}, ('SAMPLER',)),
    'SamplerCustomAdvanced': ({'noise':'NOISE','guider':'GUIDER','sampler':'SAMPLER',
        'sigmas':'SIGMAS','latent_image':'LATENT'}, ('LATENT','LATENT')),
    'VAEDecode': ({'samples':'LATENT','vae':'VAE'}, ('IMAGE',)),
    'VAEDecodeAudio': ({'samples':'LATENT','vae':'VAE'}, ('AUDIO',)),
}


def port_type(port):
    return 'COMBO' if isinstance(port[0], list) else port[0]


def enum_options(port):
    return port[0] if isinstance(port[0],list) else port[1].get('options',[]) if len(port)>1 else []


def schema_digest(schema):
    """Digest execution-relevant schema, excluding display/provider descriptions."""
    relevant = {k:schema.get(k) for k in ('input','input_order','output','output_is_list')}
    validate_schema_numbers(relevant)
    return native_digest(relevant)


def validate_schema_numbers(value):
    """Reject nonfinite JSON numbers before consuming native schema options."""
    if isinstance(value, float) and not math.isfinite(value):
        incompatible('Native schema options must use finite JSON numbers.')
    if isinstance(value, dict):
        for item in value.values():
            validate_schema_numbers(item)
    elif isinstance(value, list):
        for item in value:
            validate_schema_numbers(item)


def native_digest(value):
    # Runtime schema/graph integer widgets include UINT64_MAX. They are not
    # Project JSON records; Project seeds stay decimal strings without changes.
    return digest_bytes(json.dumps(value,ensure_ascii=False,sort_keys=True,
                                  separators=(',',':'),allow_nan=False).encode('utf-8'))


def incompatible(message):
    fail('MODEL_INCOMPATIBLE',message,stage='prepare')


def enum_value(schemas, cls, port, value):
    try:
        choices = enum_options(schemas[cls]['input']['required'][port])
    except (KeyError, TypeError, IndexError, AttributeError):
        incompatible(f'Missing native schema: {cls}.{port}.')
    if not isinstance(choices,list) or value not in choices:
        incompatible(f'Select an available, verified {cls}.{port}: {value}.')


def validate_native_profile(profile, schemas, core_revision, *, structural=True):
    if profile['core_revision'] not in CORES or core_revision != profile['core_revision']:
        incompatible('This exact core revision has no checked native adapter profile.')
    if profile['base_family'] != 'ref2va' or profile['memory_policy'] != 'one_window':
        incompatible('The first adapter requires Ref2VA and one bounded window.')
    for cls,(ports,outputs) in NATIVE_PORTS.items():
        if not structural and cls in ('ModelPatchLoader','MiniMaxH3FunControlNetApply'):
            continue
        schema = schemas.get(cls,{})
        required = schema.get('input',{}).get('required',{})
        if set(required) != set(ports) or any(port_type(required[k]) != v for k,v in ports.items()):
            incompatible(f'Native required inputs changed: {cls}.')
        if tuple(schema.get('output',())) != outputs:
            incompatible(f'Native output slots changed: {cls}.')
        if profile['node_signatures'].get(cls) != schema_digest(schema):
            incompatible(f'Profile schema fingerprint differs: {cls}.')
    components = profile['components']
    roles = ('model','clip','video_vae','audio_vae') + (('patch',) if structural else ())
    for role in roles:
        c = components.get(role,{})
        if not all(c.get(k) for k in ('filename','revision','digest','format','metadata')):
            incompatible(f'Unverified checkpoint metadata or revision: {role}.')
        if c['format'] != 'comfy-native' or c['digest'].get('algorithm') != 'sha256' or len(c['digest'].get('hex','')) != 64:
            incompatible(f'Checkpoint fingerprint/format is unsupported: {role}.')
        if (Path(c['filename']).name!=COMPONENTS[role][0] or c['revision']!=REVISION or
            c['digest']['hex']!=COMPONENTS[role][1]):
            incompatible(f'Unknown checkpoint combination/revision: {role}.')
    for role,cls,port in (('model','UNETLoader','unet_name'),('clip','CLIPLoader','clip_name'),
                          ('video_vae','VAELoader','vae_name'),('audio_vae','VAELoader','vae_name')):
        enum_value(schemas,cls,port,components[role]['filename'])
    enum_value(schemas,'CLIPLoader','type','minimax')
    base = components['model']['metadata']
    if base.get('family') != 'ref2va' or base.get('num_layers') != 50 or base.get('video_channels') != 24:
        incompatible('The base metadata does not match the checked H3 architecture.')
    if base.get('adaln') not in ('basis','full') or base.get('time_embed_dim') != (8 if base.get('adaln') == 'basis' else 2688):
        incompatible('Unknown base AdaLN layout.')
    sampling = profile['sampling']
    expected = {'sampler_name','scheduler','steps','denoise','shift_video','shift_audio'}
    if set(sampling) != expected:
        incompatible('Sampling parameters must be explicit and complete.')
    enum_value(schemas,'KSamplerSelect','sampler_name',sampling['sampler_name'])
    enum_value(schemas,'BasicScheduler','scheduler',sampling['scheduler'])
    if type(sampling['steps']) is not int or not 1 <= sampling['steps'] <= 10000:
        incompatible('Invalid native steps.')
    for key in ('denoise','shift_video','shift_audio'):
        v = sampling[key]
        if type(v) not in (int,float) or not math.isfinite(v):
            incompatible(f'Invalid sampling value: {key}.')
    if sampling['denoise'] != 1.0 or not (0 <= sampling['shift_video'] <= 100 and 0 <= sampling['shift_audio'] <= 100):
        incompatible('This first profile uses full native denoise and bounded shifts.')
    if structural:
        enum_value(schemas,'ModelPatchLoader','name',components['patch']['filename'])
        patch,branch = components['patch']['metadata'],profile['control_branch']
        version = branch.get('version')
        if version!='union-v1':
            incompatible('The pinned initial control file is Union v1; v2 requires its own reviewed component/profile revision.')
        count,norm = {'union-v1':(5,'pre_norm'),'union-v2':(10,'post_norm')}.get(version,(0,None))
        layers = list(range(0,50,50//count)) if count else []
        expected_branch = {'version':version,'block_count':count,'injection_layers':layers,
                           'input_channels':49,'adaln':base['adaln'],'normalization_mode':norm}
        if not count or branch != expected_branch:
            incompatible('Control v1/v2, injection, channels or normalization are unsupported.')
        for key in ('block_count','injection_layers','input_channels','normalization_mode','adaln'):
            if patch.get(key) != expected_branch[key]:
                incompatible(f'Control checkpoint differs from the selected branch: {key}.')
        if patch.get('time_embed_dim') != base['time_embed_dim'] or patch.get('metadata_adaln') != ('adaln_basis' if base['adaln'] == 'basis' else None):
            incompatible('Base and control checkpoint AdaLN metadata are incompatible.')
        if patch.get('missing_keys') != [] or patch.get('unexpected_keys') != []:
            incompatible('Incomplete or unknown control checkpoint key layout.')
    return profile
