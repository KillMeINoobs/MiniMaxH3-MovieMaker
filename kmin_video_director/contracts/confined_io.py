"""Local path checks and cooperative publication leases.

Supported input is a stable, user-selected local folder with regular files.
These standard Python operations are not an OS isolation boundary.
"""
from contextlib import contextmanager
import errno
import os
from pathlib import Path
import stat

from ..errors import ContractError, fail
from .validation import validate_locator


def _resolve_path(value):
    """Normalize paths without exposing resolver errors or machine paths."""
    try:
        return Path(value).resolve()
    except (OSError, RuntimeError, TypeError, ValueError):
        # Python 3.11 reports symlink loops as RuntimeError; newer versions may
        # use OSError. Suppress the context, which can include an absolute path.
        raise ContractError("PROJECT_IO_ERROR", "The project path cannot be resolved.") from None


def selected_path(project_root, relative_path):
    validate_locator(relative_path)
    root = _resolve_path(project_root)
    try:
        is_folder = root.is_dir()
    except (OSError, ValueError):
        raise ContractError("PROJECT_IO_ERROR", "The selected project folder cannot be opened.") from None
    if not is_folder:
        fail("PROJECT_IO_ERROR", "Select an existing local project folder.")
    target = _resolve_path(root.joinpath(*relative_path.split("/")))
    if not target.is_relative_to(root) or target == root:
        fail("INVALID_LOCATOR", "The locator escapes the selected project folder.")
    return target


class Parent:
    def __init__(self, path):
        self.path = path

    def read(self, name):
        path = self.path / name
        # Check before opening: a stable FIFO/device must never enter a blocking
        # read. Folder/file replacement during this operation is unsupported.
        if not stat.S_ISREG(path.stat().st_mode):
            fail("PROJECT_IO_ERROR", "Project input must be a regular file.")
        return path.open("rb")

    def exists(self, name):
        try:
            if not stat.S_ISREG((self.path / name).stat().st_mode):
                fail("INVALID_LOCATOR", "Project destination must be a regular file.")
            return True
        except FileNotFoundError:
            return False

    def publish(self, temporary, name, overwrite):
        source, target = self.path / temporary, self.path / name
        if overwrite:
            os.replace(source, target)
        else:
            # Atomic no-clobber publication; unsupported filesystems return an
            # I/O error without falling back to a partial destination write.
            os.link(source, target)

    def unlink(self, name):
        try:
            (self.path / name).unlink()
        except FileNotFoundError:
            pass


@contextmanager
def local_parent(project_root, relative_path, *, create=False):
    target = selected_path(project_root, relative_path)
    if create:
        target.parent.mkdir(parents=True, exist_ok=True)
    yield Parent(target.parent), target.name


@contextmanager
def publication_lease(parent, name):
    # Existing cooperative guard, not a filesystem security boundary. Never
    # unlink the persistent lease: replacement would split concurrent writers.
    lock_path = parent.path / ".kvd-save.lock"
    try:
        if lock_path.is_symlink() or not stat.S_ISREG(lock_path.stat().st_mode):
            fail("PROJECT_IO_ERROR", "Project publication lease must be a regular file.")
    except FileNotFoundError:
        pass
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o600)
    acquired = False
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            fail("PROJECT_IO_ERROR", "Project publication lease must be a regular file.")
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            acquired = True
        except OSError as error:
            if error.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                fail("PROJECT_BUSY", "Another writer is publishing this project; retry after it completes.",
                     stage="save", retryable=True)
            raise
        yield
    finally:
        try:
            if acquired:
                if os.name == "nt": msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                else: fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
