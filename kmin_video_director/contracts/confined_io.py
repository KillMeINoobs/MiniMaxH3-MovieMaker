"""Directory identity protection and same-destination publication leases.

Windows holds non-delete-sharing handles to every path component. POSIX uses
directory-relative descriptors and O_NOFOLLOW. Optional native APIs are imported
only on their platform; no third-party runtime dependency is required.
"""
from contextlib import contextmanager
import errno
import os
from pathlib import Path
import stat

from ..errors import fail
from .validation import validate_locator


def _win_api():
    import ctypes
    from ctypes import wintypes
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    api.CreateFileW.restype = wintypes.HANDLE
    api.GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
    api.GetFileAttributesW.restype = wintypes.DWORD
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    return ctypes, api


def _win_open(path, access, share, disposition, *, directory=False):
    ctypes, api = _win_api()
    # OPEN_REPARSE_POINT; directories additionally require BACKUP_SEMANTICS.
    flags = 0x00200000 | (0x02000000 if directory else 0)
    handle = api.CreateFileW(str(path), access, share, None, disposition, flags, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        attributes = api.GetFileAttributesW(str(path))
        if attributes == 0xFFFFFFFF:
            raise ctypes.WinError(ctypes.get_last_error())
        if attributes & 0x400:  # FILE_ATTRIBUTE_REPARSE_POINT
            fail("INVALID_LOCATOR", "Project I/O cannot follow a reparse point.")
        if bool(attributes & 0x10) != directory:
            fail("PROJECT_IO_ERROR", "The project path has an unexpected file type.")
        return handle
    except BaseException:
        api.CloseHandle(handle)
        raise


def _win_fd(path, *, write=False):
    import msvcrt
    _, api = _win_api()
    # Readers deny write/delete sharing while the bytes are read. A lease file
    # shares read/write with other contenders, but denies replacement/deletion.
    handle = _win_open(path, 0xC0000000 if write else 0x80000000,
                       3 if write else 1, 4 if write else 3)
    try:
        return msvcrt.open_osfhandle(handle, (os.O_RDWR if write else os.O_RDONLY) | os.O_BINARY)
    except BaseException:
        api.CloseHandle(handle)
        raise


class Parent:
    def __init__(self, path, fd=None):
        self.path, self.fd = path, fd

    def read(self, name):
        fd = _win_fd(self.path / name) if os.name == "nt" else os.open(
            name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=self.fd)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                fail("PROJECT_IO_ERROR", "Project input must be a regular file.")
            return os.fdopen(fd, "rb")
        except BaseException:
            os.close(fd)
            raise

    def exists(self, name):
        try:
            info = os.stat(self.path / name, follow_symlinks=False) if os.name == "nt" else os.stat(
                name, dir_fd=self.fd, follow_symlinks=False)
            if not stat.S_ISREG(info.st_mode):
                fail("INVALID_LOCATOR", "Project destination must be a regular file.")
            return True
        except FileNotFoundError:
            return False

    def publish(self, temporary, name, overwrite):
        if os.name == "nt":
            source, target = self.path / temporary, self.path / name
            if overwrite:
                os.replace(source, target)
            else:
                os.link(source, target)
        elif overwrite:
            os.replace(temporary, name, src_dir_fd=self.fd, dst_dir_fd=self.fd)
        else:
            os.link(temporary, name, src_dir_fd=self.fd, dst_dir_fd=self.fd, follow_symlinks=False)

    def unlink(self, name):
        try:
            if os.name == "nt": os.unlink(self.path / name)
            else: os.unlink(name, dir_fd=self.fd)
        except FileNotFoundError:
            pass


@contextmanager
def protected_parent(project_root, relative_path, *, create=False):
    validate_locator(relative_path)
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise FileNotFoundError("Selected project folder is unavailable")
    target = root.joinpath(*relative_path.split("/"))
    handles = []
    try:
        if os.name == "nt":
            _, api = _win_api()
            for directory in (*reversed(target.parent.parents), target.parent):
                if create and directory.is_relative_to(root) and directory != root:
                    try: os.mkdir(directory)
                    except FileExistsError: pass
                # No FILE_SHARE_DELETE: rename/replacement of this component is
                # denied for the entire staging, read/check and publication.
                # FILE_LIST_DIRECTORY participates in Windows sharing checks;
                # metadata-only access (0/READ_ATTRIBUTES) does not block rename.
                handles.append(_win_open(directory, 1, 3, 3, directory=True))
            yield Parent(target.parent), target.name
        else:
            if not hasattr(os, "O_NOFOLLOW"):
                fail("PROJECT_IO_ERROR", "This platform lacks protected directory-relative I/O.")
            current = os.open(target.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            handles.append(current)
            path = Path(target.anchor)
            for component in target.parent.parts[1:]:
                path = path / component
                if create and path.is_relative_to(root) and path != root:
                    try: os.mkdir(component, dir_fd=current)
                    except FileExistsError: pass
                current = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
                handles.append(current)
            yield Parent(target.parent, current), target.name
    finally:
        for handle in reversed(handles):
            if os.name == "nt": api.CloseHandle(handle)
            else: os.close(handle)


@contextmanager
def publication_lease(parent, name):
    # Persistent empty metadata file; the OS releases the lease on process exit.
    # Never unlink it on release: replacing its inode would split writer locks.
    # One lease per parent also covers case/short-name aliases on Windows.
    lock_name = ".kvd-save.lock"
    fd = _win_fd(parent.path / lock_name, write=True) if os.name == "nt" else os.open(
        lock_name, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=parent.fd)
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
