# -*- encoding: utf-8 -*-
"""Test module

"""
import os
import io
from random import randbytes, choices
import string
import time
import tarfile
import pyzstd
import struct
import logging

from Crypto.Random import get_random_bytes
from filelock import Timeout

import cofferfile
from cofferfile import META_CHUNK, META_SIZE
from pycoffer import CofferInfo, Coffer, open as store_open
from aesfile.zstd import open as zstd_open
from aesfile.tar import TarFile as TarZstdAesFile

import pytest

def test_store_info(random_path, random_name):
    sinfo = CofferInfo('titi', store_path=random_path)
    assert repr(sinfo).startswith('<Coffer')
    assert sinfo.mtime is None
    assert sinfo.atime is None
    assert sinfo.filesize is None

def test_store_open(random_path, random_name):
    key = get_random_bytes(16)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with store_open(dataf, mode='wb', container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        assert repr(ff).startswith('<Coffer')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert ff.readable

    with store_open(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    with open(dataf, "rb") as fdata:
        with store_open(fdata, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
            assert data == ff.read('file1%s.data'%random_name)
            assert data2 == ff.read('file2%s.data'%random_name)
            assert not ff.writable
            assert ff.readable

def test_store_basic(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG, logger="pycoffer")
    key = get_random_bytes(16)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        assert repr(ff).startswith('<Coffer')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert ff.readable

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    data3 = randbytes(6589)
    with Coffer(dataf, "ab", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        mtime2 = ff.mtime
        assert mtime2 > mtime

    with Coffer(dataf, "r", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)

    with Coffer(dataf, "ab", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        ff.delete('file3%s.data'%random_name)
        ff.append(data2a, 'file2%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        with pytest.raises(OSError):
            data = ff.read('file3%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 + data2a == ff.read('file2%s.data'%random_name)

    data4 = randbytes(54128)
    with Coffer(dataf, "ab", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        ff.write(data4, '4/file%s.data'%random_name)

    dataf2 = os.path.join(random_path, 'file2%s.out'%random_name)
    with open(dataf2, "wb") as out:
        out.write(os.urandom(127 * 50))
    with open(dataf2, "rb") as ff:
        ddataf2 = ff.read()

    with Coffer(dataf, "ab", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is False

    fff = None
    with Coffer(dataf, "rb", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        fff = ff
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 + data2a == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert data4 == ff.read('4/file%s.data'%random_name)
    assert fff.closed is True

    with pytest.raises(OSError):
        with Coffer(dataf, "xb", container_class=TarZstdAesFile,
                container_params={'aes_key':key}) as ff:
            ff.write(data3, 'file3%s.data'%random_name)
            assert ff.closed is False

    with Coffer(dataf, "ab", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        ddir = os.path.join(random_path, 'bckp%s'%random_name)
        os.makedirs(ddir)
        dataf2 = os.path.join(ddir, 'file22%s.data'%random_name)
        with open(dataf2, "wb") as out:
            out.write(os.urandom(127 * 50))
        with open(dataf2, "rb") as fff:
            ddataf2 = fff.read()
        dataf3 = os.path.join(ddir, 'file33%s.data'%random_name)
        with open(dataf3, "wb") as out:
            out.write(os.urandom(127 * 50))
        with open(dataf3, "rb") as fff:
            ddataf3 = fff.read()
        ff.add(ddir, 'test', replace=False)

    with Coffer(dataf, "rb", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        edir = os.path.join(random_path, 'extract%s'%random_name)
        os.makedirs(edir)
        ff.extract('test/file22%s.data'%(random_name),edir)
        assert ddataf2 == ff.read('test/file22%s.data'%random_name)
        # ~ assert ff.modified is False
        # ~ assert data2 + data2a == ff.read('file2%s.data'%random_name)

        # ~ ff.write(data, os.path.join('bckp%s/file11%s.data'%(random_name, random_name)))
        # ~ ff.write(data2, os.path.join('bckp%s/file22%s.data'%(random_name, random_name)))
        # ~ assert ff.modified is False
        # ~ assert ff.modified is False

    with Coffer(dataf, "ab", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        dddir = os.path.join(random_path, 'bckp2_%s'%random_name)
        ddir = os.path.join(random_path, '%s/test'%dddir)
        os.makedirs(ddir)
        dataf2 = os.path.join(ddir, 'file222%s.data'%random_name)
        with open(dataf2, "wb") as out:
            out.write(os.urandom(127 * 50))
        with open(dataf2, "rb") as fff:
            ddataf2 = fff.read()
        dataf3 = os.path.join(ddir, 'file333%s.data'%random_name)
        with open(dataf3, "wb") as out:
            out.write(os.urandom(127 * 50))
        with open(dataf3, "rb") as fff:
            ddataf3 = fff.read()
        ff.add(dddir, 'test2', replace=False)

    with Coffer(dataf, "rb", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        edir = os.path.join(random_path, 'extract2%s'%random_name)
        os.makedirs(edir)
        ff.extract('test2/test/file222%s.data'%(random_name), edir)
        with pytest.raises(FileNotFoundError):
            ff.read(edir+'/test2/file222%s.data'%(random_name))
        with open(edir+'/test2/test/file222%s.data'%(random_name), "rb") as fff:
            assert ddataf2 == fff.read()

def test_store_basic_recurse(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG, logger="pycoffer")
    key = get_random_bytes(16)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        assert repr(ff).startswith('<Coffer')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)

    edir = os.path.join(random_path, 'extract%s'%random_name)
    with Coffer(dataf, "rb", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        os.makedirs(edir)
        ff.extractall(edir)
    assert os.path.isfile(os.path.join(edir, 'file1%s.data'%random_name))
    assert os.path.isfile(os.path.join(edir, 'file2%s.data'%random_name))

    with Coffer(dataf, "ab", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        ff.add(edir)

    with Coffer(dataf, "rb", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        print(ff.getmembers())

    e2dir = os.path.join(random_path, 'extract2%s'%random_name)
    with Coffer(dataf, "rb", container_class=TarZstdAesFile,
            container_params={'aes_key':key}) as ff:
        os.makedirs(e2dir)
        ff.extractall(e2dir)

    assert os.path.isfile(os.path.join(e2dir, 'extract%s'%random_name, 'file1%s.data'%random_name))
    assert os.path.isfile(os.path.join(e2dir, 'extract%s'%random_name, 'file2%s.data'%random_name))

def test_store_no_flush(random_path, random_name):
    key = get_random_bytes(16)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
        assert ff.modified is False
        ff.write(data, 'file1%s.data'%random_name)
        assert ff.modified is True
        ff.write(data2, 'file2%s.data'%random_name)
        assert ff.writable
        assert ff.readable

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
        assert ff.modified is False
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable
        mtime = ff.mtime

    data3 = randbytes(6589)
    with Coffer(dataf, "ab", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False,
            backup='.bak') as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        mtime2 = ff.mtime
        assert mtime2 == mtime
        ff.flush()
        mtime3 = ff.mtime
        assert mtime3 > mtime2
        ff.flush(force=False)
        mtime4 = ff.mtime
        assert mtime3 == mtime4
        ff.flush()
        mtime5 = ff.mtime
        assert mtime5 > mtime4

    assert os.path.isfile(dataf + '.bak')

    with Coffer(dataf, "r", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
        assert ff.modified is False
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert ff.modified is False

    with Coffer(dataf, "ab", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
        assert ff.modified is False
        ff.delete('file3%s.data'%random_name)
        assert ff.modified is True
        ff.append(data2a, 'file2%s.data'%random_name)
        assert ff.modified is True

    dataf2 = os.path.join(random_path, 'file2%s.out'%random_name)
    with open(dataf2, "wb") as out:
        out.write(os.urandom(127 * 50))
    with open(dataf2, "rb") as ff:
        ddataf2 = ff.read()

    with Coffer(dataf, "ab", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is True

    with pytest.raises(FileExistsError):
        with Coffer(dataf, "ab", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
            ff.add(dataf2, '5/file%s.data'%random_name, replace=False)

    with Coffer(dataf, "ab", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is True

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
        with pytest.raises(OSError):
            data = ff.read('file3%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 + data2a == ff.read('file2%s.data'%random_name)

    data4 = randbytes(54128)
    with Coffer(dataf, "ab", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        ff.write(data4, '4/file%s.data'%random_name)

    fff = None
    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
        fff = ff
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 + data2a == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert data4 == ff.read('4/file%s.data'%random_name)
    assert fff.closed is True
    with pytest.raises(io.UnsupportedOperation):
        assert fff.readable
    with pytest.raises(io.UnsupportedOperation):
        assert fff.modified
    with pytest.raises(io.UnsupportedOperation):
        assert fff.writable
    with pytest.raises(io.UnsupportedOperation):
        fff._check_can_write()
    with pytest.raises(io.UnsupportedOperation):
        fff._check_can_read()

    with pytest.raises(OSError):
        with Coffer(dataf, "xb", container_class=TarZstdAesFile, container_params={'aes_key':key}, auto_flush=False) as ff:
            ff.write(data3, 'file3%s.data'%random_name)
            assert ff.closed is False

def test_store_exception(random_path, random_name):
    key = get_random_bytes(16)
    data = randbytes(2487)
    data2 = randbytes(1536)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        ff.write(data, 'file1%s.data'%random_name)
        with pytest.raises(FileNotFoundError):
            ff.add('badfile', 'file2%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        with pytest.raises(FileNotFoundError):
            assert data2 == ff.read('file2%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':None}) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(None, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(OSError):
        with Coffer('notafile.bad', "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
            assert ff.mtime is None
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(dataf, "rt", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(dataf, "rt", container_params={'aes_key':key}) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(dataf, "zz", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(dataf, None, container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(dataf, 'rb', container_class=TarZstdAesFile, container_params=None) as ff:
            assert data == ff.read('file1%s.data'%random_name)

def test_store_strings(random_path, random_name):
    key = get_random_bytes(16)
    length = 684
    data = [
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
    ]
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        ff.writelines(data, 'file1%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        assert data == ff.readlines('file1%s.data'%random_name)

def test_store_secure_basic(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG)
    key = get_random_bytes(16)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        assert repr(ff).startswith('<Coffer')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert ff.readable

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    data3 = randbytes(6589)
    with Coffer(dataf, "ab", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        mtime2 = ff.mtime

    assert mtime2 > mtime

    with Coffer(dataf, "r", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)

    with Coffer(dataf, "ab", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        ff.delete('file3%s.data'%random_name)
        ff.append(data2a, 'file2%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        with pytest.raises(OSError):
            data = ff.read('file3%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 + data2a == ff.read('file2%s.data'%random_name)

    data4 = randbytes(54128)
    with Coffer(dataf, "ab", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        ff.write(data4, '4/file%s.data'%random_name)

    dataf2 = os.path.join(random_path, 'file2%s.out'%random_name)
    with open(dataf2, "wb") as out:
        out.write(os.urandom(127 * 50))
    with open(dataf2, "rb") as ff:
        ddataf2 = ff.read()

    with Coffer(dataf, "ab", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is False

    fff = None
    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        fff = ff
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 + data2a == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert data4 == ff.read('4/file%s.data'%random_name)
    assert fff.closed is True

    with pytest.raises(OSError):
        with Coffer(dataf, "xb", container_class=TarZstdAesFile, container_params={'aes_key':key},
                secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
            ff.write(data3, 'file3%s.data'%random_name)
            assert ff.closed is False

    extdir = os.path.join(random_path, 'extract_tar%s'%random_name)
    os.makedirs(extdir, exist_ok=True)
    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        ff.extractall(extdir)

    extdir = os.path.join(random_path, 'extract_tar2%s'%random_name)
    os.makedirs(extdir, exist_ok=True)
    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        ff.extract('file3%s.data'%random_name, extdir)

def test_store_secure_tmp(random_path, random_name):
    key = get_random_bytes(16)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        assert repr(ff).startswith('<Coffer')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert ff.readable

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key},
            secure_open=zstd_open, secure_params={'aes_key': key}) as ff:
        for member in ff.getmembers():
            with zstd_open(member.path, 'rb', aes_key=key) as fff:
                datar = fff.read()
                if member.name == 'file1%s.data'%random_name:
                    assert data == datar
                elif member.name == 'file2%s.data'%random_name:
                    assert data2 == datar
            with pytest.raises(ValueError):
                with zstd_open(member.path, 'rb', aes_key=None) as fff:
                    assert fff.read() is not None

def test_coffer_pickle(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG, logger="pycoffer")
    key = get_random_bytes(16)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    data = {'rand1':data2, 'rand2':data2a}

    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        ff.pickle_dump(data, 'data.pickle')

    with Coffer(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        assert data == ff.pickle_load('data.pickle')

def test_coffer_lock(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG, logger="pycoffer")
    key = get_random_bytes(16)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    data = {'rand1':data2, 'rand2':data2a}

    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', lock_type='rw', lock_timeout=0.2,
            container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        ff.pickle_dump(data, 'data.pickle')

    with Coffer(dataf, "wb", lock_type='rw', lock_timeout=0.2,
            container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        with pytest.raises(Timeout):
            with Coffer(dataf, "wb", lock_type='rw', lock_timeout=0.2,
                    container_class=TarZstdAesFile, container_params={'aes_key':key}) as fff:
                assert data == ff.pickle_load('data.pickle')

    with Coffer(dataf, "wb", lock_type='rw', lock_timeout=0.2,
            container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        with pytest.raises(Timeout):
            with Coffer(dataf, "rb", lock_type='rw', lock_timeout=0.2,
                    container_class=TarZstdAesFile, container_params={'aes_key':key}) as fff:
                assert data == ff.pickle_load('data.pickle')

    with Coffer(dataf, "rb", lock_type='rw', lock_timeout=0.2,
            container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        with pytest.raises(Timeout):
            with Coffer(dataf, "rb", lock_type='rw', lock_timeout=0.2,
                    container_class=TarZstdAesFile, container_params={'aes_key':key}) as fff:
                assert data == ff.pickle_load('data.pickle')

    with Coffer(dataf, "rb", lock_type='rw', lock_timeout=0.2,
            container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        with pytest.raises(Timeout):
            with Coffer(dataf, "wb", lock_type='rw', lock_timeout=0.2,
                    container_class=TarZstdAesFile, container_params={'aes_key':key}) as fff:
                assert data == ff.pickle_load('data.pickle')

    with Coffer(dataf, "wb", lock_type='w', lock_timeout=0.2,
            container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        with pytest.raises(Timeout):
            with Coffer(dataf, "wb", lock_type='w', lock_timeout=0.2,
                    container_class=TarZstdAesFile, container_params={'aes_key':key}) as fff:
                assert data == ff.pickle_load('data.pickle')

    with Coffer(dataf, "wb", lock_type='w', lock_timeout=0.2,
            container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        with Coffer(dataf, "rb", lock_type='w', lock_timeout=0.2,
                container_class=TarZstdAesFile, container_params={'aes_key':key}) as fff:
            assert data == ff.pickle_load('data.pickle')

    with Coffer(dataf, "rb", lock_type='w', lock_timeout=0.2,
            container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        with Coffer(dataf, "wb", lock_type='w', lock_timeout=0.2,
                container_class=TarZstdAesFile, container_params={'aes_key':key}) as fff:
            assert data == ff.pickle_load('data.pickle')

    with Coffer(dataf, "rb", lock_type='w', lock_timeout=0.2,
            container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        with Coffer(dataf, "rb", lock_type='w', lock_timeout=0.2,
                container_class=TarZstdAesFile, container_params={'aes_key':key}) as fff:
            assert data == ff.pickle_load('data.pickle')

def test_store_mtime(random_path, random_name):
    key = get_random_bytes(16)
    data1 = randbytes(2487)
    data2 = randbytes(1536)
    data3 = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)
    dataf1 = 'file1%s.data'%random_name
    dataf2 = 'file2%s.data'%random_name
    dataf3 = 'file3%s.data'%random_name

    with store_open(dataf, mode='wb', container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        ff.write(data1, dataf1)
        ff.write(data2, dataf2)
        members = ff.getmembers()
        for memb in members:
            if memb.name.startswith('file1'):
                mtime1 = memb.mtime
                atime1 = memb.atime
            elif memb.name.startswith('file2'):
                mtime2 = memb.mtime
                atime2 = memb.atime
        # ~ print(members)

    with store_open(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        assert data1 == ff.read(dataf1)
        assert data2 == ff.read(dataf2)
        members = ff.getmembers()
        for memb in members:
            if memb.name.startswith('file1'):
                assert mtime1 == memb.mtime
                # ~ assert atime1 == memb.atime
            elif memb.name.startswith('file2'):
                assert mtime2 == memb.mtime
                # ~ assert atime2 == memb.atime

    with open(os.path.join(random_path, dataf3), 'wb') as f:
        f.write(data3)
    os.utime(os.path.join(random_path, dataf3), (time.time() - 60, time.time() - 120))
    atime3 = os.path.getatime(os.path.join(random_path, dataf3))
    mtime3 = os.path.getmtime(os.path.join(random_path, dataf3))

    with store_open(dataf, mode='wb', container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        ff.add(os.path.join(random_path, dataf3), dataf3)

    with store_open(dataf, "rb", container_class=TarZstdAesFile, container_params={'aes_key':key}) as ff:
        assert data1 == ff.read(dataf1)
        assert data2 == ff.read(dataf2)
        assert data3 == ff.read(dataf3)
        members = ff.getmembers()
        for memb in members:
            if memb.name.startswith('file1'):
                assert mtime1 == memb.mtime
                # ~ assert atime1 == memb.atime
            elif memb.name.startswith('file2'):
                assert mtime2 == memb.mtime
                # ~ assert atime2 == memb.atime
            elif memb.name.startswith('file3'):
                assert mtime3 == memb.mtime
                # ~ assert atime3 == memb.atime
