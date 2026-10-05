"""Bounded native Canny. No alternate edge algorithm replaces absent dependencies."""
import hashlib
from importlib import metadata
from pathlib import Path
import math

from ..contracts import cache_key, cache_locator, digest_json
from ..contracts.worker import ControlArtifact
from ..errors import fail
from ..media.backend import bounded_operation
from .storage import checked_media_path, check_geometry, raw_frames, write_raw

BACKEND_ID = 'comfy-native-canny'
VERSION = 'kvd-native-canny/1.0.0'
SOURCE_SHA256 = 'a08dbf4b1690042adfadf4b6ea0b183064c2a7bb4982d6576aa5f23a16d762ce'
BACKEND_VERSIONS = frozenset(('source-b87fe48','source-daeb5e5'))


def thresholds(low,high):
    if (type(low) not in (int,float) or type(high) not in (int,float) or
        not math.isfinite(low) or not math.isfinite(high) or not .01 <= low < high <= .99):
        fail('INVALID_RECORD','Native Canny requires finite 0.01 <= low < high <= 0.99 thresholds.')


def native_backend():
    try:
        import torch
        from comfy_extras import nodes_canny
        from kornia.filters import canny
        kornia_version = metadata.version('kornia')
    except (ImportError,metadata.PackageNotFoundError):
        fail('DEPENDENCY_MISSING','BuildControl requires native Comfy Canny, Torch and Kornia; no fallback is installed.',stage='control')
    try:
        source = Path(nodes_canny.__file__).read_bytes().replace(b'\r\n',b'\n')
    except OSError:
        fail('DEPENDENCY_MISSING','Native Canny source provenance cannot be checked.',stage='control')
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        fail('MODEL_INCOMPATIBLE','Native Canny source differs from the checked implementation.',stage='control')
    return torch,nodes_canny.Canny,{'torch':str(torch.__version__),'kornia':kornia_version,
                                  'native_source_sha256':SOURCE_SHA256}


def native_canny_rgb(frame,width,height,low,high,backend,*,context):
    thresholds(low,high)
    if len(frame) != width*height*3:
        fail('FRAME_COUNT_MISMATCH','Canny input must be exact RGB N/H/W/3 geometry.')
    torch,Canny,_ = backend
    context.cancellation.check()
    image = torch.frombuffer(bytearray(frame),dtype=torch.uint8).reshape(1,height,width,3).to(dtype=torch.float32)/255
    # Actual native operation retains its device/dtype and algorithm management.
    output = Canny.execute(image,low,high)[0]
    context.cancellation.check()
    if tuple(output.shape) != (1,height,width,3) or not bool(torch.isfinite(output).all()):
        fail('FRAME_COUNT_MISMATCH','Native Canny returned invalid RGB geometry or values.')
    if not bool(((output == 0) | (output == 1)).all()):
        fail('MODEL_INCOMPATIBLE','Native Canny returned a nonbinary structural map.')
    result = output.detach().to(device='cpu',dtype=torch.float32).mul(255).to(dtype=torch.uint8).contiguous()
    return result.numpy().tobytes()


@bounded_operation
def build_control(prepared,control,*,context):
    context.cancellation.check()
    spatial = check_geometry(prepared.spatial,prepared.frame_count)
    if prepared.media['role'] != 'prepared_video':
        fail('INVALID_RECORD','Control extraction requires a prepared-video artifact.')
    video = prepared.media['probe']['video']
    if (video is None or video['width'] != spatial['canvas_width'] or video['height'] != spatial['canvas_height']
            or video['rate'] != {'num':24,'den':1} or video['vfr']):
        fail('FRAME_COUNT_MISMATCH','Prepared video must match exact native canvas geometry and 24 FPS.')
    if control['type'] == 'off' and not control['enabled']:
        return ControlArtifact(prepared.window_id,control.id,None,prepared.spatial.id,prepared.frame_count)
    if control['type'] != 'canny' or not control['enabled']:
        fail('UNSUPPORTED_CAPABILITY','Choose enabled Canny or explicit structural off.')
    recipe = control['backend']
    if (recipe['id'] != BACKEND_ID or recipe['version'] not in BACKEND_VERSIONS or recipe['model_digest'] is not None
            or recipe['temporal_policy'] != 'fixed_parameters' or control['preprocess_version'] not in (VERSION,'canny/1')):
        fail('UNSUPPORTED_CAPABILITY','The declared Canny backend/version is unsupported.')
    params = recipe['parameters']
    if set(params) != {'low_threshold','high_threshold'}:
        fail('INVALID_RECORD','Canny exposes only its two declared normalized thresholds.')
    low,high = params['low_threshold'],params['high_threshold']
    thresholds(low,high)
    rect = spatial['content_rect']
    from ..adapters.native_h3.media_bridge import integer_limit
    budget = integer_limit(context,'working_set_bytes',268435456)
    if budget <= 0 or rect['width']*rect['height']*160 + spatial['canvas_width']*spatial['canvas_height']*6 > budget:
        fail('RESOURCE_LIMIT','The content frame exceeds the explicit Canny working-set budget.')
    checked_media_path(prepared.media,context)
    backend = native_backend()
    key = cache_key('control',{'prepared':prepared.media['fingerprint']['digest'],'spatial':spatial,
        'frame_count':prepared.frame_count,'backend':recipe,'implementation':backend[2]},algorithm_version=VERSION)
    relative = cache_locator('control',key,suffix='rgb')['path']
    width,height = spatial['canvas_width'],spatial['canvas_height']
    def maps():
        previous,previous_map = None,None
        for frame in raw_frames(prepared.media,prepared.frame_count,width,height,context):
            context.cancellation.check()
            if frame == previous:
                yield previous_map
                continue
            content = b''.join(frame[((rect['y']+y)*width+rect['x'])*3:((rect['y']+y)*width+rect['x']+rect['width'])*3]
                               for y in range(rect['height']))
            edges = native_canny_rgb(content,rect['width'],rect['height'],low,high,backend,context=context)
            padded = bytearray(width*height*3)
            for y in range(rect['height']):
                start = ((rect['y']+y)*width+rect['x'])*3
                padded[start:start+rect['width']*3] = edges[y*rect['width']*3:(y+1)*rect['width']*3]
            previous,previous_map = frame,bytes(padded)
            yield previous_map
    implementation_version = VERSION+'+'+digest_json(backend[2])['hex']
    media = write_raw(maps(),relative,prepared.frame_count,width,height,'control_map',implementation_version,context)
    from ..adapters.native_h3.media_bridge import write_json
    write_json({'version':VERSION,'native_implementation':backend[2],'recipe':control.to_dict(),
        'prepared_digest':prepared.media['fingerprint']['digest'],'spatial':spatial,
        'frame_count':prepared.frame_count,'map':media.to_dict(),'gpu':'not_performed'},
        cache_locator('control',key,suffix='json')['path'],context)
    return ControlArtifact(prepared.window_id,control.id,media,prepared.spatial.id,prepared.frame_count,media)
