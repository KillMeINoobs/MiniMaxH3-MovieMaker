"""Synthetic safetensors headers; no checkpoint contents/model loading."""
import json
import struct

import pytest

from kmin_video_director.contracts import ContractError
from kmin_video_director.contracts.worker import CancellationFlag, OperationContext
from kmin_video_director.adapters.native_h3.checkpoints import read_header, architecture_metadata


def write_header(path,tensors,metadata=None):
    offset=0
    header={'__metadata__':metadata or {}}
    for name,shape in tensors.items():
        size=4
        for dim in shape: size*=dim
        header[name]={'dtype':'F32','shape':shape,'data_offsets':[offset,offset+size]}
        offset+=size
    payload=json.dumps(header).encode()
    with path.open('wb') as stream:
        stream.write(struct.pack('<Q',len(payload)))
        stream.write(payload)
        stream.write(bytes(offset))


def patch(count=5):
    t={'control_proj_in.weight':[4,196], 'control_proj_in.bias':[4]}
    for b in range(count):
        for suffix,shape in {'after_proj.weight':[4,4],'after_proj.bias':[4],
            'adaln_proj.linear.weight':[72,8],'adaln_proj.linear.bias':[72],
            'attn.qkv_proj.weight':[12,4],'attn.q_norm.weight':[4],'attn.k_norm.weight':[4],
            'attn.out_proj.weight':[4,4],'mlp.fc1.weight':[8,4],'mlp.fc2.weight':[4,4],
            'norm1.weight':[4],'norm2.weight':[4]}.items(): t[f'control_blocks.{b}.{suffix}']=shape
    t['control_blocks.0.before_proj.weight']=[4,4]
    t['control_blocks.0.before_proj.bias']=[4]
    return t


def test_header_fingerprint_and_architecture_are_observed(tmp_path):
    path=tmp_path/'synthetic.safetensors'
    write_header(path,patch(),{'minimax_h3_fun_controlnet':'adaln_basis'})
    ctx=OperationContext(tmp_path,CancellationFlag(),{})
    header,fp=read_header(path,context=ctx)
    m=architecture_metadata(header,'patch')
    assert m['block_count']==5 and m['injection_layers']==[0,10,20,30,40]
    assert m['time_embed_dim']==8 and m['normalization_mode']=='pre_norm'
    assert fp['byte_size']==path.stat().st_size
    assert m['missing_keys']==m['unexpected_keys']==[]


@pytest.mark.parametrize('fault',['blocks','adaln','channels','keys','truncated','offset','cancel'])
def test_unknown_or_incomplete_layouts_fail_honestly(tmp_path,fault):
    tensors=patch()
    if fault=='blocks': tensors['control_blocks.9.after_proj.weight']=[4,4]
    if fault=='adaln': tensors['control_blocks.0.adaln_proj.linear.weight']=[72,2688]
    if fault=='channels': tensors['control_proj_in.weight']=[4,192]
    if fault=='keys': del tensors['control_blocks.2.attn.q_norm.weight']
    path=tmp_path/'synthetic.safetensors'
    write_header(path,tensors,{'minimax_h3_fun_controlnet':'adaln_basis'})
    if fault=='truncated': path.write_bytes(path.read_bytes()[:-1])
    if fault=='offset': path.write_bytes(struct.pack('<Q',100_000_000)+b'{}')
    ctx=OperationContext(tmp_path,CancellationFlag(),{})
    if fault=='cancel': ctx.cancellation.cancel()
    with pytest.raises(ContractError):
        header,_=read_header(path,context=ctx)
        architecture_metadata(header,'patch')


def test_v2_post_norm_is_explicit(tmp_path):
    path=tmp_path/'synthetic-v2.safetensors'
    write_header(path,patch(10),{'minimax_h3_fun_controlnet':'adaln_basis','inpaint_masked_pixel_mode':'post_norm'})
    h,_=read_header(path,context=OperationContext(tmp_path,CancellationFlag(),{}))
    m=architecture_metadata(h,'patch')
    assert m['block_count']==10 and m['injection_layers']==list(range(0,50,5)) and m['normalization_mode']=='post_norm'
