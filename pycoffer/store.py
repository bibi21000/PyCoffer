# -*- encoding: utf-8 -*-
""" Store your files in a ztsd/tar based archive.

Interface "compatible" with tar

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import os
import time
import tempfile
import threading
from contextlib import contextmanager
import shutil
import tarfile
import io
from filelock import FileLock

from fernetfile.zstd import FernetFile as ZstdFernetFile
from fernetfile.tar import TarFile as TarZstdFernetFile
from fernetfile.zstd import CHUNK_SIZE, READ, WRITE, APPEND, EXCLUSIVE

_open = open

# ~ class TarZstdFernetFile(tarfile.TarFile):
    # ~ """The container of the store. Based on TarFfile with encryption"""

    # ~ def __init__(self, name, mode='r', fileobj=None, fernet_key=None, **kwargs):
        # ~ """Init the TarZstdFernetFile"""
        # ~ level_or_option = kwargs.pop('level_or_option', None)
        # ~ zstd_dict = kwargs.pop('zstd_dict', None)
        # ~ chunk_size = kwargs.pop('chunk_size', CHUNK_SIZE)
        # ~ self.fernet_file = ZstdFernetFile(name, mode, fileobj=fileobj,
            # ~ fernet_key=fernet_key, level_or_option=level_or_option,
                # ~ zstd_dict=zstd_dict, chunk_size=chunk_size, **kwargs)
        # ~ try:
            # ~ super().__init__(fileobj=self.fernet_file, mode=mode.replace('b', ''), **kwargs)

        # ~ except Exception:
            # ~ self.fernet_file.close()
            # ~ raise

    # ~ def close(self):
        # ~ """Close the TarZstdFernetFile"""
        # ~ try:
            # ~ super().close()

        # ~ finally:
            # ~ if self.fernet_file is not None:
                # ~ self.fernet_file.close()

    # ~ def __repr__(self):
        # ~ """ """
        # ~ s = repr(self.fernet_file)
        # ~ return '<TarZstdFernet ' + s[1:-1] + ' ' + hex(id(self)) + '>'


class StoreInfo():
    """ """

    def __init__(self, name, store_path=None):
        """A representation of the file in tmp"""
        self.store_path = store_path
        sname = str(name)
        if sname[0] == '/':
            self.name = sname[1:]
        else:
            self.name = sname
        dirs = self.name.rsplit('/', 1)
        if len(dirs) > 1 :
            self.subdir = '%s'%dirs[0]
            self.dirpath = os.path.join(self.store_path, self.subdir)
        else:
            self.subdir = None
            self.dirpath = self.store_path
        self.path = os.path.join(self.store_path, '%s'%self.name)

    @property
    def mtime(self):
        """The mtime of the file in tmp"""
        if os.path.isfile(self.path):
            return os.path.getmtime(self.path)
        return None

    def __repr__(self):
        """ """
        s = repr(self.name)
        return '<CofferStoreInfo ' + s[1:-1] + ' ' + hex(id(self)) + '>'

class CofferStore():
    """ """

    filename = None

    def __init__(self, filename=None, mode=None, fileobj=None,
            auto_flush=True, backup=None,
            secure_open=None, secure_params=None,
            container_class=None, container_params=None, **kwargs):
        """Constructor for the FernetFile class.

        At least one of fileobj and filename must be given a
        non-trivial value.

        The new class instance is based on fileobj, which can be a regular
        file, an io.BytesIO object, or any other object which simulates a file.
        It defaults to None, in which case filename is opened to provide
        a file object.

        When fileobj is not None, the filename argument is only used to be
        included in the gzip file header, which may include the original
        filename of the uncompressed file.  It defaults to the filename of
        fileobj, if discernible; otherwise, it defaults to the empty string,
        and in this case the original filename is not included in the header.

        The mode argument can be any of 'r', 'rb', 'a', 'ab', 'w', 'wb', 'x', or
        'xb' depending on whether the file will be read or written.  The default
        is the mode of fileobj if discernible; otherwise, the default is 'rb'.
        A mode of 'r' is equivalent to one of 'rb', and similarly for 'w' and
        'wb', 'a' and 'ab', and 'x' and 'xb'.

        The fernet_key argument is the Fernet key used to crypt/decrypt data.
        Encryption is done by chunks to reduce memory footprint. The default
        chunk_size is 64KB.

        Files are stored in clear mode when opening archive (in a directory in /tmp).
        You can give a "secured open" command to avoid that (in dev)

        Everytime data are written in archive, it is flushed to file : this means
        that thar archive is compressed and crypted. You can change this with auto_flush.
        Data will be flushed only on close.

        This store is thread safe, this allows you to flush from a timer for example.

        If you want to backup archive before flushing it, pass extention to this parameter.
        """
        if container_params is None:
            raise ValueError("Invalid containe params: {!r}".format(container_params))
        if mode is None or ('t' in mode or 'U' in mode):
            raise ValueError("Invalid mode: {!r}".format(mode))
        if mode and 'b' not in mode:
            mode += 'b'
        if mode.startswith('r'):
            self.mode = READ
        elif mode.startswith('w'):
            self.mode = WRITE
        elif mode.startswith('a'):
            self.mode = APPEND
        elif mode.startswith('x'):
            self.mode = EXCLUSIVE
        else:
            raise ValueError("Invalid mode: {!r}".format(mode))
        self._lock = threading.Lock()
        # ~ self.fernet_key = fernet_key
        self.container_class = container_class
        self.container_params = container_params
        if self.container_class is None:
            self.container_class = TarZstdFernetFile
        self.kwargs = kwargs
        if fileobj is not None:
            self.filename = fileobj.name
            self.fileobj = fileobj
        else:
            self.filename = filename
            self.fileobj = None
        if self.filename is None:
            raise ValueError("Invalid filename: {!r}".format(filename))
        self.backup = backup
        self.auto_flush = auto_flush
        self._lockfile = FileLock(self.filename+'.lock')
        self.secure_open = _open
        self.secure_params = secure_params
        if secure_open is not None:
            self.secure_open = secure_open
        if self.secure_params is None:
            self.secure_params = {}
        self.dirpath = None
        self._dirctime = None
        self._dirmtime = None

    def __repr__(self):
        """A repr of the store"""
        s = repr(self.filename)
        return '<CofferStore ' + s[1:-1] + ' ' + hex(id(self)) + '>'

    def _check_not_closed(self):
        """Check if the store is closed"""
        if self.closed:
            raise io.UnsupportedOperation("I/O operation on closed file")

    def _check_can_write(self):
        """Check we can write in store"""
        if self.closed:
            raise io.UnsupportedOperation("I/O operation on closed file")
        if not self.writable:
            raise io.UnsupportedOperation("File not open for writing")

    # ~ def _check_can_read(self):
        # ~ """Check we can read in store"""
        # ~ if self.closed:
            # ~ raise io.UnsupportedOperation("I/O operation on closed file")
        # ~ if not self.readable:
            # ~ raise io.UnsupportedOperation("File not open for reading")

    def __enter__(self):
        """Enter context manager"""
        return self.open()

    def __exit__(self, type, value, traceback):
        """Exit context manager"""
        self.close()

    def open(self):
        """Open the store with a lock"""
        self._lockfile.acquire()
        file_exists = os.path.isfile(self.filename)
        if file_exists:
            if self.mode == EXCLUSIVE:
                raise FileExistsError('File already exists %s' % self.filename)
        else:
            if self.mode == READ:
                raise FileNotFoundError('File not found %s' % self.filename)
        self.dirpath = tempfile.mkdtemp(prefix=".fernet_")
        if file_exists:
            with self.container_class(self.filename, mode='rb', fileobj=self.fileobj,
                **self.container_params,
                **self.kwargs) as tff:
                tff.extractall(self.dirpath)
        self._dirctime = self._dirmtime = time.time_ns()
        return self

    def _write_store(self):
        """Write the store in filename"""
        self._check_can_write()
        with self._lock:
            if self.backup is not None:
                if os.path.isfile(self.filename + self.backup) is True:
                    os.remove(self.filename + self.backup)
                shutil.move(self.filename, self.filename + self.backup)

            with self.container_class(self.filename, mode='wb', fileobj=self.fileobj,
                **self.container_params,
                **self.kwargs) as tff:
                for member in self.getmembers():
                    tff.add(member.path, arcname=member.name)

            self._dirctime = self._dirmtime = time.time_ns()

    def getmembers(self):
        """Get members or the store"""
        members = []
        for root, dirs, files in os.walk(self.dirpath):
            for fname in files:
                aname = os.path.join( root[len(self.dirpath):], fname )
                members.append(StoreInfo(aname, store_path=self.dirpath))
        return members

    def close(self):
        """Close the store. If file is open for writing, the store is rewriting"""
        if self.writable:
            self._write_store()
        shutil.rmtree(self.dirpath)
        self.dirpath = None
        self._dirctime = None
        self._dirmtime = None
        self._lockfile.release()

    def flush(self, force=True):
        """Flush data to store if needed. Unless force is True """
        if force is False and self.modified is False:
            return
        self._write_store()

    @contextmanager
    def file(self, arcname=None, mode='rb', encoding=None):
        """Return a file descriptor on arcname"""
        fffile = None
        with self._lock:
            if isinstance(arcname, StoreInfo):
                finfo = arcname
            else:
                finfo = StoreInfo(arcname, store_path=self.dirpath)
            try:
                if finfo.subdir is not None:
                    os.makedirs(os.path.join(self.dirpath, finfo.subdir), exist_ok=True)
                fffile = ffile = self.secure_open(finfo.path, mode=mode, encoding=encoding, **self.secure_params)
                yield ffile
                ffile.close()
                ffile = None
                if mode.startswith(('w', 'a', 'x')):
                    self._dirmtime = time.time_ns()
            finally:
                if fffile is not None:
                    fffile.close()
                    fffile = None

        if self.auto_flush is True and mode.startswith(('w', 'a', 'x')):
            self.flush()

    def add(self, filename, arcname=None, replace=True):
        """Add file as arcname. If arcname exists, it is replaced by default.
        Otherwise an exception is raised"""
        with self._lock:
            self._check_can_write()
            if isinstance(arcname, StoreInfo):
                finfo = arcname
            else:
                finfo = StoreInfo(arcname, store_path=self.dirpath)

            file_exists = os.path.isfile(finfo.path)
            if file_exists is True and replace is False:
                raise FileExistsError('File already exists %s' % self.filename)

            if file_exists is True:
                self._delete(arcinfo=finfo)

            if finfo.subdir is not None:
                os.makedirs(os.path.join(self.dirpath, finfo.subdir), exist_ok=True)

            with _open(filename, 'rb') as ff, self.secure_open(finfo.path, mode='wb', **self.secure_params) as sf:
                sf.write(ff.read())
            self._dirmtime = time.time_ns()

        if self.auto_flush is True:
            self.flush()

    def extractall(self, path='.', members=None):
        """Extract all files to path"""
        with self._lock:
            self._check_not_closed()
            os.makedirs(path, exist_ok=True)
            if members is None:
                members = self.getmembers()
            for member in members:
                print(member.subdir)
                if member.subdir is not None:
                    os.makedirs(os.path.join(path, member.subdir), exist_ok=True)

                with self.secure_open(member.path, mode='rb', **self.secure_params) as fin, \
                    _open(os.path.join(path, member.name), mode='wb') as fout:
                        fout.write(fin.read())

    def _delete(self, arcinfo=None):
        """Delete file in store without lock"""
        self._check_can_write()
        os.remove(arcinfo.path)
        self._dirmtime = time.time_ns()

    def delete(self, arcname=None):
        """Delete file in store"""
        with self._lock:
            if isinstance(arcname, StoreInfo):
                finfo = arcname
            else:
                finfo = StoreInfo(arcname, store_path=self.dirpath)
            self._delete(arcinfo=finfo)
        if self.auto_flush is True:
            self.flush()

    def append(self, data, arcname=None):
        """Append data to arcname"""
        self._check_can_write()
        with self.file(arcname=arcname, mode='ab') as nf:
            nf.write(data)

    def write(self, data, arcname=None):
        """Write data to arcname"""
        self._check_can_write()
        with self.file(arcname=arcname, mode='wb') as nf:
            nf.write(data)

    def read(self, arcname=None):
        """Read data from arcname"""
        self._check_not_closed()
        with self.file(arcname=arcname, mode='rb') as nf:
            return nf.read()

    def readlines(self, arcname=None, encoding='UTF-8'):
        """Read a list of lines from arcname"""
        self._check_not_closed()
        lines = []
        with self.file(arcname=arcname, mode='rt', encoding=encoding) as nf:
            for line in nf:
                lines.append(line.rstrip())
        return lines

    def writelines(self, lines, arcname=None, encoding='UTF-8'):
        """Write a list of lines to arcname"""
        self._check_can_write()
        with self.file(arcname=arcname, mode='wt', encoding=encoding) as nf:
            for line in lines:
                nf.write(line + '\n')

    @property
    def mtime(self):
        """Last modification time read from stream, or None."""
        if os.path.isfile(self.filename) is True:
            return os.path.getmtime(self.filename)
        return None

    @property
    def modified(self):
        """Archive has been updated but not flushed."""
        self._check_not_closed()
        return self._dirctime < self._dirmtime

    @property
    def closed(self):
        """True if this file is closed."""
        return self.dirpath is None

    @property
    def readable(self):
        """Return whether the file was opened for reading."""
        self._check_not_closed()
        return self.mode == READ

    @property
    def writable(self):
        """Return whether the file was opened for writing."""
        self._check_not_closed()
        return self.mode == WRITE or self.mode == APPEND \
            or self.mode == EXCLUSIVE


def open(filename, mode="rb",
        auto_flush=True, backup=None,
        secure_open=None, secure_params=None,
        container_class=None, container_params=None, **kwargs):
    """Open a CofferStore file in binary mode.

    The filename argument can be an actual filename (a str or bytes object), or
    an existing file object to read from or write to.

    The mode argument can be "r", "rb", "w", "wb", "x", "xb", "a" or "ab" for
    binary mode.

    For binary mode, this function is equivalent to the FernetFile constructor:
    FernetFile(filename, mode, fernet_key). In this case, the encoding, errors
    and newline arguments must not be provided.


    """
    if "t" in mode:
        raise ValueError("Invalid mode: %r" % (mode,))

    if isinstance(filename, (str, bytes, os.PathLike)):
        binary_file = CofferStore(filename, mode=mode,
            secure_open=secure_open, secure_params=secure_params,
            container_class=container_class, container_params=container_params,
            **kwargs)
    elif hasattr(filename, "read") or hasattr(filename, "write"):
        binary_file = CofferStore(None, mode=mode, fileobj=filename,
            secure_open=secure_open, secure_params=secure_params,
            container_class=container_class, container_params=container_params,
            **kwargs)
    else:
        raise TypeError("filename must be a str or bytes object, or a file")

    return binary_file
