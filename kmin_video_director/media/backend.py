"""Explicit lazy external backend, bounded pipes and ordinary local artifacts."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import threading
import time

from ..contracts import MediaRef, canonical_bytes
from ..contracts.confined_io import selected_path
from ..errors import ContractError, fail


def limit(context, key, default):
    try:
        value = int(context.versions.get(key, str(default)))
        if value <= 0:
            raise ValueError
        return value
    except (ValueError, TypeError):
        fail('RESOURCE_LIMIT', 'Resource limits must be positive integers.', details={'limit': key})


def regular(path):
    try:
        if not stat.S_ISREG(path.stat().st_mode):
            fail('PROJECT_IO_ERROR', 'Media input must be an ordinary regular file.')
    except FileNotFoundError:
        raise ContractError('SOURCE_MISSING', 'The selected media file is missing.', stage='media') from None
    except OSError:
        raise ContractError('PROJECT_IO_ERROR', 'The selected media file cannot be opened.', stage='media') from None
    return path


def hash_file(path, context):
    regular(path)
    h = hashlib.sha256()
    try:
        with path.open('rb') as f:
            while True:
                context.cancellation.check()
                block = f.read(65536)
                if not block:
                    break
                h.update(block)
        return {'algorithm': 'sha256', 'hex': h.hexdigest()}
    except OSError:
        raise ContractError('PROJECT_IO_ERROR', 'Media content could not be read.', stage='media') from None


def check_media(media, context):
    context.cancellation.check()
    path = regular(selected_path(context.asset_root, media['locator']['path']))
    fp = media['fingerprint']
    if path.stat().st_size != fp['byte_size'] or hash_file(path, context) != fp['digest']:
        fail('SOURCE_CHANGED', 'Media content differs from its recorded fingerprint.', stage='media')
    return path


_operation_budget = ContextVar('kvd_media_operation_budget', default=None)


def bounded_operation(callback):
    @wraps(callback)
    def requested(*args, context, **kwargs):
        active = _operation_budget.get()
        if active is not None and active.context is context:
            return callback(*args, context=context, **kwargs)
        budget = Budget(context)
        token = _operation_budget.set(budget)
        try:
            result = callback(*args, context=context, **kwargs)
            budget.check()
            return result
        finally:
            _operation_budget.reset(token)
    return requested


class Budget:
    def __new__(cls, context):
        active = _operation_budget.get()
        return active if active is not None and active.context is context else super().__new__(cls)

    def __init__(self, context):
        if hasattr(self, 'context'):
            return
        self.context = context
        self.paths = []
        self.peak_bytes = 0
        self.quota = limit(context, 'disk_quota_bytes', 4 * 1024**3)

    def check(self):
        self.context.cancellation.check()
        total = 0
        for path in set(self.paths):
            try:
                total += path.stat().st_size
            except FileNotFoundError:
                pass
        self.peak_bytes = max(self.peak_bytes, total)
        if total > self.quota:
            fail('RESOURCE_LIMIT', 'The operation exceeded its disk quota.', stage='media')

    def reserve(self, amount):
        self.check()
        if amount + sum(p.stat().st_size for p in set(self.paths) if p.exists()) > self.quota or amount > shutil.disk_usage(self.context.asset_root).free:
            fail('RESOURCE_LIMIT', 'Insufficient declared disk budget or free space.', stage='media')


@contextmanager
def target(locator, context, budget):
    path = selected_path(context.asset_root, locator['path'])
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix='kvd-', suffix='.partial', dir=path.parent)
        os.close(fd)
        temporary = Path(name)
        budget.paths.append(temporary)
        yield temporary
        budget.check()
        os.replace(temporary, path)
        budget.paths[budget.paths.index(temporary)] = path
    except OSError:
        raise ContractError('PROJECT_IO_ERROR', 'The owned media artifact could not be published.', stage='media') from None
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass  # Unpublished leftovers are never active cache receipts.


def write_json(locator, value, context, budget):
    with target(locator, context, budget) as temporary:
        temporary.write_bytes(canonical_bytes(value))


def read_json(locator, context):
    path = regular(selected_path(context.asset_root, locator['path']))
    if path.stat().st_size > 8 * 1024**2:
        fail('RESOURCE_LIMIT', 'The media manifest exceeds its bounded JSON limit.')
    try:
        from ..contracts.serialization import parse_json
        return parse_json(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise ContractError('INVALID_RECORD', 'The media manifest cannot be read.') from None


def peak_rss(process):
    # Ordinary process-memory measurement. No machine inventory or foreign process access.
    if os.name != 'nt':
        return None
    import ctypes
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('faults', wintypes.DWORD)] + [(n, ctypes.c_size_t) for n in
            ('peak', 'working', 'paged_peak', 'paged', 'nonpaged_peak', 'nonpaged', 'pagefile', 'pagefile_peak')]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    function = ctypes.windll.psapi.GetProcessMemoryInfo
    function.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
    if function(wintypes.HANDLE(int(process._handle)), ctypes.byref(counters), counters.cb):
        return counters.peak
    return None


@contextmanager
def process(argv, context, budget, *, stdin=None, stdout=subprocess.PIPE):
    context.cancellation.check()
    failure = []
    stop = threading.Event()
    with tempfile.TemporaryFile(dir=context.asset_root) as diagnostics:
        try:
            p = subprocess.Popen(argv, stdin=stdin, stdout=stdout, stderr=diagnostics,
                shell=False, creationflags=0x08000000 if os.name == 'nt' else 0)
        except (OSError, ValueError):
            raise ContractError('UNSUPPORTED_CAPABILITY', 'The selected media backend could not start.', stage='media') from None
        p.kvd_report = {'peak_working_set_bytes': None, 'elapsed_seconds': 0.0}
        started = time.monotonic()
        timeout = limit(context, 'timeout_seconds', 1200)
        def watch():
            while not stop.wait(0.02):
                observed = peak_rss(p)
                if observed is not None:
                    p.kvd_report['peak_working_set_bytes'] = max(observed, p.kvd_report['peak_working_set_bytes'] or 0)
                try:
                    budget.check()
                    if diagnostics.tell() > 1024**2 or time.monotonic() - started > timeout:
                        fail('RESOURCE_LIMIT', 'The media operation exceeded its time or diagnostic budget.', stage='media')
                except BaseException as error:
                    failure.append(error)
                    if p.poll() is None:
                        p.kill()  # Only this operation-owned subprocess.
                    return
        watcher = threading.Thread(target=watch, daemon=True)
        watcher.start()
        try:
            yield p
            if p.stdin is not None and not p.stdin.closed:
                p.stdin.close()
            p.wait()
            if failure:
                raise failure[0]
            budget.check()
            if p.returncode:
                fail('PROJECT_IO_ERROR', 'The selected media backend failed.', stage='media',
                     details={'exit_code': p.returncode})
        except (BrokenPipeError, OSError):
            if failure:
                raise failure[0] from None
            raise ContractError('PROJECT_IO_ERROR', 'The media backend pipe failed.', stage='media') from None
        except BaseException:
            if failure:
                raise failure[0] from None
            raise
        finally:
            stop.set()
            if p.poll() is None:
                p.kill()
            p.wait()
            watcher.join()
            for pipe in (p.stdin, p.stdout):
                if pipe is not None:
                    try:
                        pipe.close()
                    except OSError:
                        pass
            p.kvd_report['elapsed_seconds'] = round(time.monotonic() - started, 6)


def capture(argv, context, *, maximum=1024**2):
    budget = Budget(context)
    with process(argv, context, budget) as p:
        data = p.stdout.read(maximum + 1)
        if len(data) > maximum:
            fail('RESOURCE_LIMIT', 'Backend metadata exceeds its bounded limit.')
    return data


def backend(context):
    paths = []
    for key in ('ffmpeg_path', 'ffprobe_path'):
        value = context.versions.get(key)
        if not value or not Path(value).is_absolute() or not Path(value).is_file():
            fail('UNSUPPORTED_CAPABILITY', 'Select existing absolute FFmpeg and ffprobe executable paths explicitly.',
                 details={'setting': key})
        paths.append(str(value))
    ffmpeg, ffprobe = paths
    versions = {}
    for name, path in zip(('ffmpeg', 'ffprobe'), paths):
        text = capture([path, '-version'], context).decode('utf-8', 'replace')
        first = text.splitlines()[0]
        versions[name] = first[:96]
        versions[name + '_build_digest'] = {'algorithm': 'sha256', 'hex': hashlib.sha256(text.encode()).hexdigest()}
    return ffmpeg, ffprobe, versions


def media_ref(locator, role, probe, versions, context):
    path = regular(selected_path(context.asset_root, locator['path']))
    digest = hash_file(path, context)
    from ..contracts import stable_id
    return MediaRef.from_dict({'id': stable_id('media', digest, role, probe), 'role': role, 'locator': locator,
        'fingerprint': {'digest': digest, 'byte_size': path.stat().st_size, 'mtime_ns': str(path.stat().st_mtime_ns),
            'video_stream': probe['video']['stream_index'] if probe['video'] else None,
            'audio_stream': probe['audio']['stream_index'] if probe['audio'] else None,
            'probe_version': versions['ffprobe'], 'decoder_version': versions['ffmpeg']},
        'probe': probe, 'availability': 'available', 'error': None})


def with_role(media, role):
    from ..contracts import stable_id
    data = media.to_dict()
    data.update(id=stable_id('media', data['fingerprint']['digest'], role, data['probe']), role=role)
    return MediaRef.from_dict(data)
