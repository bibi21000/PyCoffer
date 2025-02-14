# -*- encoding: utf-8 -*-
""" Store your files in a ztsd/tar based archive.

Interface "compatible" with tar

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import os

from pycoffer import Coffer
from naclfile.zstd import open as zstd_open
from fernetfile.tar import TarFile as TarZstdFernetFile

class CofferStore(Coffer):
    """ """

    def __init__(self, filename=None, mode=None, fileobj=None,
            auto_flush=True, backup=None,
            fernet_key=None, secret_key=None,
            **kwargs):
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
        super().__init__(filename=filename, mode=mode, fileobj=fileobj,
            auto_flush=auto_flush, backup=backup,
            secure_open=zstd_open, secure_params={'secret_key': secret_key},
            container_class=TarZstdFernetFile, container_params={'fernet_key': fernet_key},
            **kwargs)

    def __repr__(self):
        """A repr of the store"""
        s = repr(self.filename)
        return '<CofferStore ' + s[1:-1] + ' ' + hex(id(self)) + '>'

def open(filename, mode="rb",
        auto_flush=True, backup=None,
        secret_key=None, fernet_key=None,
        **kwargs):
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
            secret_key=secret_key, fernet_key=fernet_key,
            **kwargs)
    elif hasattr(filename, "read") or hasattr(filename, "write"):
        binary_file = CofferStore(None, mode=mode, fileobj=filename,
            secret_key=secret_key, fernet_key=fernet_key,
            **kwargs)
    else:
        raise TypeError("filename must be a str or bytes object, or a file")

    return binary_file
