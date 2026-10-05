"""Small raw RGB manifests for structural maps and constructed CPU inputs.

This is a versioned disk representation, never a tensor in Project JSON.
External media decoding belongs to the explicit native H3 media bridge.
"""
import hashlib
import os
import stat
import tempfile

from ..contracts import MediaRef, digest_json, resolve_locator, stable_id
from ..errors import ContractError, fail

RAW_CODEC = 'kvd-rgb24'
RAW_VERSION = 'kvd-rgb24/1.0.0'


def check_count(n):
    if type(n) is not int or not 124 <= n <= 345 or (n-5) % 17:
        fail('FRAME_COUNT_MISMATCH', 'A native window needs 124..345 frames on the 17k+5 lattice.')


def check_geometry(spatial, n):
    check_count(n)
    s = spatial.to_dict()
    w,h = s['canvas_width'],s['canvas_height']
    r = s['content_rect']
    if w % 32 or h % 32 or r['x']+r['width'] > w or r['y']+r['height'] > h:
        fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'The content rectangle must fit the exact grid32 canvas.')
    if r['width'] != s['fitted_width'] or r['height'] != s['fitted_height']:
        fail('UNSUPPORTED_EXPORT_DIMENSIONS', 'The declared fitted content and crop rectangle differ.')
    return s


def checked_media_path(media, context):
    context.cancellation.check()
    if media['availability'] != 'available':
        fail('SOURCE_MISSING', 'The explicitly selected media artifact is unavailable.')
    path = resolve_locator(context.asset_root, media['locator']['path'])
    size, hash = 0, hashlib.sha256()
    try:
        if not stat.S_ISREG(path.stat().st_mode):
            fail('SOURCE_MISSING', 'Media input must be an ordinary regular file.')
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024), b''):
                context.cancellation.check()
                size += len(chunk)
                hash.update(chunk)
    except OSError:
        raise ContractError('SOURCE_MISSING','The selected media artifact cannot be read.') from None
    if size != media['fingerprint']['byte_size'] or hash.hexdigest() != media['fingerprint']['digest']['hex']:
        fail('SOURCE_CHANGED','The media artifact no longer matches its content fingerprint.')
    return path


def raw_frames(media, n, width, height, context):
    path = checked_media_path(media,context)
    if media['probe']['video']['codec'] != RAW_CODEC:
        # The bridge has its own reviewed-integration gate and lazy backend.
        from ..adapters.native_h3.media_bridge import decode_rgb
        yield from decode_rgb(media,n,width,height,context=context)
        return
    if path.stat().st_size != n*width*height*3:
        fail('FRAME_COUNT_MISMATCH','Raw RGB bytes do not match the declared N/H/W/3 geometry.')
    with path.open('rb') as stream:
        for _ in range(n):
            context.cancellation.check()
            frame = stream.read(width*height*3)
            if len(frame) != width*height*3:
                fail('FRAME_COUNT_MISMATCH','The raw RGB window ended before its declared count.')
            yield frame
        if stream.read(1):
            fail('FRAME_COUNT_MISMATCH','The raw RGB window contains undeclared frames.')


def write_raw(frames, relative_path, n, width, height, role, version, context):
    path = resolve_locator(context.asset_root,relative_path)
    path.parent.mkdir(parents=True,exist_ok=True)
    temp = None
    count,size,hash = 0,0,hashlib.sha256()
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,suffix='.partial',delete=False) as out:
            temp = out.name
            for frame in frames:
                context.cancellation.check()
                if len(frame) != width*height*3 or count >= n:
                    fail('FRAME_COUNT_MISMATCH','The RGB writer received an invalid frame geometry or count.')
                out.write(frame)
                hash.update(frame)
                size += len(frame)
                count += 1
            if count != n:
                fail('FRAME_COUNT_MISMATCH','The RGB writer received fewer than the exact required frames.')
            out.flush()
            os.fsync(out.fileno())
        context.cancellation.check()
        os.replace(temp,path)
        temp = None
    except OSError:
        raise ContractError('PROJECT_IO_ERROR','The owned RGB artifact could not be published.',stage='control') from None
    finally:
        if temp is not None:
            try:
                os.unlink(temp)
            except OSError:
                pass
    fingerprint = {'algorithm':'sha256','hex':hash.hexdigest()}
    pts = digest_json({'representation':RAW_VERSION,'frame_count':n,'fps':{'num':24,'den':1}})
    return MediaRef.from_dict({'id':stable_id('media',role,fingerprint), 'role':role,
        'locator':{'scheme':'project_relative','path':relative_path},
        'fingerprint':{'digest':fingerprint,'byte_size':size,'mtime_ns':str(path.stat().st_mtime_ns),
            'video_stream':0,'audio_stream':None,'probe_version':version,'decoder_version':RAW_VERSION},
        'probe':{'video':{'codec':RAW_CODEC,'stream_index':0,'time_base':{'num':1,'den':24},
            'first_pts':0,'end_pts':n,'pts_digest':pts,'rate':{'num':24,'den':1},'vfr':False,
            'width':width,'height':height,'rotation':0,'sar':{'num':1,'den':1},'display_matrix':[],
            'color':'rgb','pixel_format':'rgb24'},'audio':None},'availability':'available','error':None})
