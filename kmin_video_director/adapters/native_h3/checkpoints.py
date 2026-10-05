"""Read explicitly selected safetensors headers/fingerprints, never load weights.

Recognized header architecture is source evidence; it cannot certify native
loader completeness, quantization kernels or GPU memory fit.
"""
import hashlib
import json
import math
from pathlib import Path
import re
import stat
import struct

from ...errors import fail
from .profile import incompatible

HEADER_LIMIT=16*1024*1024
DTYPE_BYTES={'BOOL':1,'U8':1,'I8':1,'F8_E4M3':1,'F8_E5M2':1,'F8_E4M3FN':1,
             'I16':2,'U16':2,'F16':2,'BF16':2,'I32':4,'U32':4,'F32':4,'I64':8,'U64':8,'F64':8}


def read_header(path,*,context):
    context.cancellation.check()
    path=Path(path)
    try:
        if not stat.S_ISREG(path.stat().st_mode): incompatible('Selected checkpoint must be a regular local file.')
        size=path.stat().st_size
        with path.open('rb') as stream:
            prefix=stream.read(8)
            if len(prefix)!=8: incompatible('Truncated safetensors header.')
            length=struct.unpack('<Q',prefix)[0]
            if not 2 <= length <= HEADER_LIMIT or length+8>size: incompatible('Unsupported safetensors header size.')
            payload=stream.read(length)
            def unique_pairs(pairs):
                out={}
                for k,v in pairs:
                    if k in out: incompatible('Duplicate safetensors metadata keys.')
                    out[k]=v
                return out
            header=json.loads(payload,object_pairs_hook=unique_pairs)
            hash=hashlib.sha256(prefix+payload)
            for block in iter(lambda:stream.read(1024*1024),b''):
                context.cancellation.check()
                hash.update(block)
    except (OSError,ValueError,UnicodeError):
        fail('MODEL_INCOMPATIBLE','The explicitly selected checkpoint header cannot be verified.')
    if not isinstance(header,dict): incompatible('Safetensors header must be an object.')
    metadata=header.get('__metadata__',{})
    if not isinstance(metadata,dict) or any(not isinstance(v,str) for v in metadata.values()):
        incompatible('Safetensors metadata fields must be strings.')
    ranges=[]
    for key,value in header.items():
        if key=='__metadata__': continue
        if not isinstance(value,dict): incompatible('Malformed safetensors tensor metadata.')
        shape=value.get('shape')
        dtype=value.get('dtype')
        offsets=value.get('data_offsets')
        if (not isinstance(shape,list) or any(type(d) is not int or d<0 for d in shape)
            or not isinstance(dtype,str) or dtype not in DTYPE_BYTES
            or not isinstance(offsets,list) or len(offsets)!=2 or any(type(d) is not int for d in offsets)):
            incompatible('Unknown safetensors dtype, shape or offsets.')
        begin,end=offsets
        if begin<0 or end<begin or end>size-length-8 or end-begin!=math.prod(shape)*DTYPE_BYTES[dtype]:
            incompatible('Checkpoint tensor sizes/offsets are incomplete or inconsistent.')
        ranges.append((begin,end))
    ranges.sort()
    if any(a[1]>b[0] for a,b in zip(ranges,ranges[1:])):
        incompatible('Checkpoint tensor byte ranges overlap.')
    return header,{'digest':{'algorithm':'sha256','hex':hash.hexdigest()},'byte_size':size}


def _shape(header,key):
    if key not in header: incompatible(f'Required checkpoint architecture key is absent: {key}.')
    return header[key]['shape']


def _blocks(header,prefix,tail):
    indices=sorted({int(m[1]) for k in header if (m:=re.fullmatch(re.escape(prefix)+r'(\d+)\.'+re.escape(tail),k))})
    if not indices or indices!=list(range(len(indices))): incompatible('Checkpoint block indices must be complete and contiguous.')
    return len(indices)


def architecture_metadata(header,role):
    meta=header.get('__metadata__',{})
    if role=='model':
        count=_blocks(header,'blocks.','attn.qkv_proj.weight')
        channels=_shape(header,'final_layer.video_out.weight')[0]//4
        hidden=_shape(header,'video_patch_proj.weight')[0]
        _shape(header,'audio_patch_proj.weight')
        if count!=50 or channels!=24: incompatible('This first source profile requires the 50-layer,24-channel H3 base.')
        basis='adaln_t_table' in header
        tdim=_shape(header,'adaln_t_table')[1] if basis else _shape(header,'time_embedder.proj_out.weight')[0]
        result={'family':'ref2va','num_layers':count,'video_channels':channels,'hidden_size':hidden,
                'adaln':'basis' if basis else 'full','time_embed_dim':tdim}
        if 'config' in meta:
            try: config=json.loads(meta['config']).get('transformer',{})
            except (ValueError,AttributeError): incompatible('Unknown base transformer metadata config.')
            observed={'num_layers':count,'latents_dim':channels,'hidden_size':hidden,'time_embed_dim':tdim}
            if any(k in config and config[k]!=v for k,v in observed.items()):
                incompatible('Base config overrides disagree with observed tensor layout.')
        return result
    if role!='patch':
        # Role identity is restricted to source-pinned filenames by the profile helper.
        return {'header_fingerprinted':True,'native_load_verified':False}
    count=_blocks(header,'control_blocks.','after_proj.weight')
    if count not in (5,10): incompatible('Only the source-described Union v1/v2 block layouts are recognized.')
    proj=_shape(header,'control_proj_in.weight')
    if len(proj)!=2 or proj[1]!=196: incompatible('Native structural control expects49 channels with1x2x2 patching.')
    hidden=proj[0]
    basis=meta.get('minimax_h3_fun_controlnet')=='adaln_basis'
    tdim=8 if basis else 2688
    required={'control_proj_in.weight','control_proj_in.bias'}
    for b in range(count):
        prefix=f'control_blocks.{b}.'
        suffixes={'adaln_proj.linear.weight','adaln_proj.linear.bias','after_proj.weight','after_proj.bias',
                  'attn.qkv_proj.weight','attn.q_norm.weight','attn.k_norm.weight','attn.out_proj.weight',
                  'mlp.fc1.weight','mlp.fc2.weight','norm1.weight','norm2.weight'}
        if b==0: suffixes|={'before_proj.weight','before_proj.bias'}
        required|={prefix+k for k in suffixes}
        for name in suffixes: _shape(header,prefix+name)
        if _shape(header,prefix+'adaln_proj.linear.weight')!=[18*hidden,tdim]:
            incompatible('Control AdaLN tensor width differs from its metadata marker.')
        if _shape(header,prefix+'after_proj.weight')!=[hidden,hidden]: incompatible('Control projection hidden widths differ.')
    # Known quantization auxiliaries remain explicitly unverified native-loader inputs.
    auxiliary=lambda k: any(k.endswith(s) for s in ('.weight_scale','.input_scale','.comfy_quant','.input_rotation','.output_rotation'))
    unexpected=sorted(k for k in header if k!='__metadata__' and k not in required and not auxiliary(k))
    if unexpected: incompatible('Unknown control checkpoint keys require a reviewed layout profile.')
    layers=list(range(0,50,50//count))
    if 'control_blocks_places' in meta:
        try: explicit=json.loads(meta['control_blocks_places'])
        except ValueError: incompatible('Invalid control injection-layer metadata.')
        if explicit!=layers: incompatible('Control injection layers differ from the source-described Union layout.')
    norm='post_norm' if meta.get('inpaint_masked_pixel_mode')=='post_norm' else 'pre_norm'
    if norm!=('pre_norm' if count==5 else 'post_norm'):
        incompatible('Union v1/v2 normalization marker is missing or inconsistent.')
    return {'block_count':count,'injection_layers':layers,'input_channels':49,'hidden_size':hidden,
        'adaln':'basis' if basis else 'full','time_embed_dim':tdim,'metadata_adaln':meta.get('minimax_h3_fun_controlnet'),
        'normalization_mode':norm,'missing_keys':[],'unexpected_keys':[],
        'native_load_verified':False}
