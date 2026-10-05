"""Ordinary failures must release only the operation's captured backend child."""
from contextlib import contextmanager
import subprocess
import traceback

import pytest

from kmin_video_director.errors import ContractError
from kmin_video_director.media import backend
from tests.media.support import context, video


@contextmanager
def captured_children(monkeypatch):
    children = []
    spawn = backend.subprocess.Popen
    with monkeypatch.context() as patch:
        def observed(*args, **kwargs):
            child = spawn(*args, **kwargs)
            children.append(child)
            return child
        patch.setattr(backend.subprocess, 'Popen', observed)
        try:
            yield children
        finally:
            # The red reproduction must not itself leave the observed leak alive.
            for child in children:
                if child.poll() is None:
                    child.kill()
                child.wait(timeout=5)
                for pipe in (child.stdin, child.stdout):
                    if pipe is not None:
                        pipe.close()


def null_decode(ctx, source, *, live=True):
    args = [ctx.versions['ffmpeg_path'], '-v', 'error', '-nostdin']
    if live:
        args += ['-re', '-stream_loop', '-1']
    return args + ['-i', str(source), '-t', '3', '-an', '-f', 'null', '-']


def assert_closed(child):
    assert child.poll() is not None
    assert child.returncode is not None  # wait/reap, not just a termination request.
    assert all(pipe is None or pipe.closed for pipe in (child.stdin, child.stdout))


@pytest.mark.parametrize('timeout', ['0', 'private-timeout-value'])
def test_invalid_timeout_does_not_spawn_a_backend_child(tmp_path, monkeypatch, timeout):
    source = video(tmp_path, count=2)
    ctx = context(tmp_path, timeout_seconds=timeout)
    with captured_children(monkeypatch) as children:
        with pytest.raises(ContractError) as raised:
            with backend.process(null_decode(ctx, source), ctx, backend.Budget(ctx)):
                pytest.fail('Invalid timeout yielded an active backend.')
        assert raised.value.code == 'RESOURCE_LIMIT'
        assert not children
        if timeout != '0':
            assert timeout not in ''.join(traceback.format_exception(raised.value))


@pytest.mark.parametrize('phase', ['constructor', 'start'])
@pytest.mark.parametrize('error_type', [RuntimeError, OSError])
def test_monitor_resource_setup_failure_is_redacted_and_closes_child(tmp_path, monkeypatch, phase, error_type):
    source = video(tmp_path, count=2)
    ctx = context(tmp_path)
    with captured_children(monkeypatch) as children:
        message = f'Synthetic monitor-{phase} failure'
        def unavailable(*args, **kwargs):
            raise error_type(message)
        if phase == 'constructor':
            monkeypatch.setattr(backend.threading, 'Thread', unavailable)
        else:
            monkeypatch.setattr(backend.threading.Thread, 'start', unavailable)
        with pytest.raises((ContractError, error_type)) as raised:
            with backend.process(null_decode(ctx, source), ctx, backend.Budget(ctx), stdin=subprocess.PIPE):
                pytest.fail('Unavailable monitor yielded an active backend.')
        assert len(children) == 1
        assert_closed(children[0])
        assert isinstance(raised.value, ContractError)
        assert raised.value.code == 'RESOURCE_LIMIT'
        assert message not in str(raised.value)
        assert message not in ''.join(traceback.format_exception(raised.value))


@pytest.mark.parametrize('phase', ['constructor', 'start'])
def test_unexpected_monitor_setup_error_stays_visible_and_closes_child(tmp_path, monkeypatch, phase):
    source = video(tmp_path, count=2)
    ctx = context(tmp_path)
    unexpected = TypeError(f'Synthetic monitor-{phase} programming error')
    with captured_children(monkeypatch) as children:
        def broken(*args, **kwargs):
            raise unexpected
        if phase == 'constructor':
            monkeypatch.setattr(backend.threading, 'Thread', broken)
        else:
            monkeypatch.setattr(backend.threading.Thread, 'start', broken)
        with pytest.raises(TypeError) as raised:
            with backend.process(null_decode(ctx, source), ctx, backend.Budget(ctx), stdin=subprocess.PIPE):
                pytest.fail('Broken monitor yielded an active backend.')
        assert len(children) == 1
        assert_closed(children[0])
        assert raised.value is unexpected
        assert str(unexpected) in ''.join(traceback.format_exception(raised.value))


def test_valid_completion_waits_and_closes_pipes(tmp_path, monkeypatch):
    source = video(tmp_path, count=2)
    ctx = context(tmp_path)
    with captured_children(monkeypatch) as children:
        with backend.process(null_decode(ctx, source, live=False), ctx, backend.Budget(ctx), stdin=subprocess.PIPE):
            pass
        assert len(children) == 1
        assert_closed(children[0])
        assert children[0].returncode == 0


def test_valid_timeout_terminates_waits_and_closes_pipes(tmp_path, monkeypatch):
    source = video(tmp_path, count=2)
    ctx = context(tmp_path, timeout_seconds=1)
    with captured_children(monkeypatch) as children:
        with pytest.raises(ContractError) as raised:
            with backend.process(null_decode(ctx, source), ctx, backend.Budget(ctx), stdin=subprocess.PIPE):
                pass
        assert raised.value.code == 'RESOURCE_LIMIT'
        assert len(children) == 1
        assert_closed(children[0])
