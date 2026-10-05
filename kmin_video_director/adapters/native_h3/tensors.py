"""Materialize only one explicitly requested structural map, with lazy native imports."""
from ...controls.storage import raw_frames
from ...errors import fail


def control_tensor(media,*,context,preview_frame=None):
    context.cancellation.check()
    video=media['probe']['video']
    if media['role']!='control_map' or not video or video['rate']!={'num':24,'den':1} or video['vfr']:
        fail('FRAME_COUNT_MISMATCH','Select an exact native structural RGB control map.')
    n=video['end_pts']-video['first_pts']
    w,h=video['width'],video['height']
    if (video['time_base']!={'num':1,'den':24} or not 124<=n<=345 or (n-5)%17 or w%32 or h%32):
        fail('FRAME_COUNT_MISMATCH','Structural map must match native N/H/W/3 grid and bounded lattice.')
    if preview_frame is not None and (type(preview_frame) is not int or not 0<=preview_frame<n):
        fail('INVALID_INTERVAL','Preview frame must lie in the prepared native window.')
    allocated=(n if preview_frame is None else 1)*w*h*3*4
    from .media_bridge import integer_limit
    if allocated+w*h*3*5 > integer_limit(context,'working_set_bytes',1073741824):
        fail('RESOURCE_LIMIT','This bounded native IMAGE exceeds its explicit working-set budget.')
    try:
        import torch
        from comfy.model_management import intermediate_device
    except ImportError:
        fail('DEPENDENCY_MISSING','Control IMAGE materialization requires the existing native Torch backend.')
    tensor=torch.empty((n if preview_frame is None else 1,h,w,3),dtype=torch.float32,device=intermediate_device())
    frames=raw_frames(media,n,w,h,context)
    try:
        for index,frame in enumerate(frames):
            context.cancellation.check()
            if any(v not in (0,255) for v in frame): fail('MODEL_INCOMPATIBLE','Native Canny map must contain binary RGB values.')
            if preview_frame is None or index==preview_frame:
                value=torch.frombuffer(bytearray(frame),dtype=torch.uint8).reshape(h,w,3).to(dtype=torch.float32)/255
                tensor[index if preview_frame is None else 0].copy_(value)
            if preview_frame is not None and index==preview_frame: break
    finally:
        frames.close()
    return tensor
