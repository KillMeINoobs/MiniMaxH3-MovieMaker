"""Explicit CPU FFmpeg I/O for one adapter window; no source discovery or inference.

Reviewed media integration re-probes final artifacts using the media owner's
global timing policy. This small bridge performs exact local RGB I/O only.
"""
from contextlib import contextmanager
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from threading import Event, Thread
import time

from ...contracts import MediaRef, digest_json, resolve_locator, stable_id
from ...controls.storage import checked_media_path
from ...errors import ContractError, fail

VERSION = 'kvd-h3-rgb-io/1.0.0'


def binaries(context):
    paths=[]
    for key in ('ffmpeg_path','ffprobe_path'):
        path=Path(context.versions.get(key,''))
        if not path.is_absolute() or not path.is_file():
            fail('DEPENDENCY_MISSING','Select existing absolute FFmpeg and ffprobe paths.',stage='decode')
        paths.append(str(path))
    return tuple(paths)


def reserve(context,expected):
    quota=integer_limit(context,'disk_quota_bytes',4*1024**3)
    if expected > quota:
        fail('RESOURCE_LIMIT','This bounded artifact exceeds its selected disk budget.')
    if shutil.disk_usage(context.asset_root).free < expected:
        fail('RESOURCE_LIMIT','The selected artifact folder lacks required free space.')
    return quota


def integer_limit(context,key,default):
    try:
        value=int(context.versions.get(key,str(default)))
    except (ValueError,TypeError):
        fail('RESOURCE_LIMIT','Use a positive integer resource budget.')
    if value<=0: fail('RESOURCE_LIMIT','Use a positive integer resource budget.')
    return value


@contextmanager
def process(args,context,*,stdin=None,stdout=subprocess.PIPE,watched=None):
    """Watchdog closes blocked owned pipes on cancellation, deadline or quota."""
    context.cancellation.check()
    try:
        timeout=float(context.versions.get('timeout_seconds','1200'))
    except (ValueError,TypeError):
        fail('RESOURCE_LIMIT','The owned backend needs a finite positive deadline.')
    quota=integer_limit(context,'disk_quota_bytes',4*1024**3)
    if not math.isfinite(timeout) or timeout <= 0:
        fail('RESOURCE_LIMIT','The owned backend needs a finite positive deadline.')
    stop=Event()
    errors=[]
    with tempfile.TemporaryFile() as stderr:
        try:
            p=subprocess.Popen(args,stdin=stdin,stdout=stdout,stderr=stderr,creationflags=0x08000000 if os.name=='nt' else 0)
        except OSError:
            fail('DEPENDENCY_MISSING','The selected external CPU backend cannot start.')
        started=time.monotonic()
        def watch():
            while not stop.wait(.05):
                try:
                    context.cancellation.check()
                    if time.monotonic()-started > timeout:
                        fail('RESOURCE_LIMIT','The owned CPU backend exceeded its deadline.')
                    if stderr.tell() > 1024*1024 or watched and Path(watched).exists() and Path(watched).stat().st_size > quota:
                        fail('RESOURCE_LIMIT','The owned backend exceeded its output budget.')
                except BaseException as error:
                    errors.append(error)
                    p.kill()
                    return
        thread=Thread(target=watch,daemon=True)
        thread.start()
        try:
            yield p
            p.wait()
            if errors: raise errors[0]
            context.cancellation.check()
            if p.returncode:
                fail('PROJECT_IO_ERROR','The selected CPU backend could not complete the bounded media operation.')
        except (BrokenPipeError,OSError):
            if errors: raise errors[0]
            fail('PROJECT_IO_ERROR','The owned CPU media pipe closed before completion.')
        finally:
            stop.set()
            if p.poll() is None: p.kill()
            p.wait()
            for pipe in (p.stdin,p.stdout):
                if pipe:
                    try: pipe.close()
                    except OSError: pass
            thread.join(timeout=1)


def _read_exact(stream,size):
    chunks=[]
    left=size
    while left:
        block=stream.read(left)
        if not block: break
        chunks.append(block)
        left-=len(block)
    return b''.join(chunks)


def decode_rgb(media,n,width,height,*,context):
    ffmpeg,_=binaries(context)
    path=checked_media_path(media,context)
    budget=integer_limit(context,'working_set_bytes',268435456)
    size=width*height*3
    if n <= 0 or n > 345 or size*3 > budget:
        fail('RESOURCE_LIMIT','RGB decode requires one bounded window and an explicit frame buffer budget.')
    args=[ffmpeg,'-v','error','-nostdin','-threads','1','-noautorotate','-i',str(path),
          '-map',f"0:{media['fingerprint']['video_stream']}",'-an','-sn','-dn','-threads','1',
          '-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
    with process(args,context) as p:
        for _ in range(n):
            context.cancellation.check()
            frame=_read_exact(p.stdout,size)
            if len(frame)!=size: fail('FRAME_COUNT_MISMATCH','Decoded RGB ended before its exact declared frame count.')
            yield frame
        if p.stdout.read(1): fail('FRAME_COUNT_MISMATCH','Decoded RGB contains additional frames or wrong geometry.')


def probe_video(path,n,width,height,context):
    _,ffprobe=binaries(context)
    args=[ffprobe,'-v','error','-select_streams','v:0','-show_streams','-show_frames',
          '-show_entries','stream=index,codec_name,time_base,width,height,pix_fmt,sample_aspect_ratio,color_space:frame=pts,duration',
          '-of','json',str(path)]
    with process(args,context) as p:
        payload=p.stdout.read(1024*1024+1)
        if len(payload)>1024*1024: fail('RESOURCE_LIMIT','Bounded native output probe exceeded its metadata budget.')
    try:
        info=json.loads(payload)
        stream,=info['streams']
        frames=info['frames']
        tb=Fraction(stream['time_base'])
        pts=[Fraction(f['pts'])*tb for f in frames]
    except (KeyError,ValueError,TypeError):
        fail('AMBIGUOUS_MEDIA_TIMING','The CPU output has no exact decoded PTS metadata.')
    if len(frames)!=n or pts != [Fraction(i,24) for i in range(n)]:
        fail('FRAME_COUNT_MISMATCH','Actual decoded useful output is not exact CFR24 coverage.')
    if (stream['width'],stream['height']) != (width,height):
        fail('UNSUPPORTED_EXPORT_DIMENSIONS','Actual decoded output geometry differs from its inverse transform.')
    pts_digest=digest_json({'version':VERSION,'pts':[{'num':t.numerator,'den':t.denominator} for t in pts]})
    return {'codec':stream['codec_name'],'stream_index':stream['index'],'time_base':{'num':tb.numerator,'den':tb.denominator},
        'first_pts':frames[0]['pts'],'end_pts':int(Fraction(n,24)/tb),'pts_digest':pts_digest,
        'rate':{'num':24,'den':1},'vfr':False,'width':width,'height':height,'rotation':0,
        'sar':{'num':1,'den':1},'display_matrix':[],'color':stream.get('color_space','unknown'),
        'pixel_format':stream['pix_fmt']}


def fingerprint_file(path,context):
    hash=hashlib.sha256()
    size=0
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            context.cancellation.check()
            size+=len(block)
            hash.update(block)
    return {'digest':{'algorithm':'sha256','hex':hash.hexdigest()},'byte_size':size,
            'mtime_ns':str(path.stat().st_mtime_ns),'video_stream':0,'audio_stream':None,
            'probe_version':VERSION,'decoder_version':VERSION}


def encode_rgb(frames,relative,n,width,height,*,context,output_width=None,output_height=None):
    ffmpeg,_=binaries(context)
    reserve(context,n*width*height*4+1024*1024)
    path=resolve_locator(context.asset_root,relative)
    path.parent.mkdir(parents=True,exist_ok=True)
    out_width,out_height=output_width or width,output_height or height
    temp=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,suffix='.partial',delete=False) as tmp:
            temp=tmp.name
        args=[ffmpeg,'-v','error','-nostdin','-y','-threads','1','-f','rawvideo','-pix_fmt','rgb24',
              '-video_size',f'{width}x{height}','-framerate','24','-i','pipe:0','-an',
              '-vf',f'scale={out_width}:{out_height}:flags=lanczos,setsar=1','-threads','1',
              '-c:v','ffv1','-level','3','-pix_fmt','gbrp','-f','nut',temp]
        count=0
        with process(args,context,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,watched=temp) as p:
            for frame in frames:
                context.cancellation.check()
                if count>=n or len(frame)!=width*height*3: fail('FRAME_COUNT_MISMATCH','Final encoder received incorrect RGB geometry/count.')
                p.stdin.write(frame)
                count+=1
            p.stdin.close()
            p.stdin=None
            if count!=n: fail('FRAME_COUNT_MISMATCH','Final encoder received an incomplete useful window.')
        video=probe_video(temp,n,out_width,out_height,context)
        context.cancellation.check()
        os.replace(temp,path)
        temp=None
        fp=fingerprint_file(path,context)
        return MediaRef.from_dict({'id':stable_id('media','render_video',fp['digest']),'role':'render_video',
            'locator':{'scheme':'project_relative','path':relative},'fingerprint':fp,
            'probe':{'video':video,'audio':None},'availability':'available','error':None})
    except OSError:
        fail('PROJECT_IO_ERROR','The bounded useful video could not be published.')
    finally:
        if temp:
            try: os.unlink(temp)
            except OSError: pass


def write_json(value,relative,context):
    path=resolve_locator(context.asset_root,relative)
    path.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')+b'\n'
    reserve(context,len(payload))
    temp=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,suffix='.partial',delete=False) as stream:
            temp=stream.name
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        context.cancellation.check()
        os.replace(temp,path)
        temp=None
    finally:
        if temp:
            try: os.unlink(temp)
            except OSError: pass
