# -*- encoding: utf-8 -*-
"""NullStore :

- No encyption at all !!! for testing only
- Coffer compression with Pyzstd
- Files use internal open
- Autoflush disable : close coffer or call flush to write update to coffer file.

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import os

from cofferfile.zstd import ZstdTarFile
from pycoffer import Coffer

class CofferNull(Coffer):
    """ """

    def __init__(self, filename=None, mode=None, fileobj=None,
            auto_flush=False, backup=None, **kwargs):
        """Constructor for the CofferNull class.

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
            container_class=ZstdTarFile, container_params={},
            **kwargs)

    def __repr__(self):
        """A repr of the store"""
        s = repr(self.filename)
        return '<CofferNull ' + s[1:-1] + ' ' + hex(id(self)) + '>'

    @classmethod
    def gen_params(cls):
        """Generate params for a new store : keys, ... as a dict"""
        return {
        }

    def crypt_open(self, filename, mode='r', **kwargs):
        """Return a crypting open function to encrypt esternal files for examples.
        Use keys of the coffer."""
        return open(filename, mode=mode, **kwargs)

def open(filename, mode="rb",
        auto_flush=False, backup=None,
        **kwargs):
    """Open a CofferMarket file in binary mode.

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
        binary_file = CofferNull(filename, mode=mode, **kwargs)
    elif hasattr(filename, "read") or hasattr(filename, "write"):
        binary_file = CofferNull(None, mode=mode, fileobj=filename,
            **kwargs)
    else:
        raise TypeError("filename must be a str or bytes object, or a file")

    return binary_file
