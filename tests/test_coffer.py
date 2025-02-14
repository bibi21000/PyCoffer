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

from cryptography.fernet import Fernet

import cofferfile
from cofferfile import META_CHUNK, META_SIZE
from pycoffer import CofferInfo, Coffer, open as store_open
from fernetfile.zstd import open as zstd_open
from fernetfile.tar import TarFile as TarZstdFernetFile

import pytest

@pytest.mark.parametrize("buff_size, file_size", [ (1024 * 64, 1024 * 512 + 13) ])
def test_zstd_extract(random_path, random_name, buff_size, file_size):
    key = Fernet.generate_key()
    fkey = Fernet(key)
    dataf = os.path.join(random_path, 'test%s.frtz'%random_name)

    dataf2 = os.path.join(random_path, 'file2%s.out'%random_name)
    with open(dataf2, "wb") as out:
        out.write(os.urandom(file_size))
    with open(dataf2, "rb") as ff:
        data = ff.read()

    with TarZstdFernetFile(dataf, mode='wb', fernet_key=key,
            chunk_size=buff_size) as ff:
        ff.add(dataf2, 'file1%s.dat'%random_name)
        assert repr(ff).startswith('<TarZstdFernet')

    with open(dataf, "rb") as ff:
        datar = ff.read()
    assert data != datar

    # Check that file is crypted
    with pytest.raises(pyzstd.ZstdError):
        with pyzstd.open(dataf, "rb") as ff:
            datar = ff.read()
    beg = 0
    datau = b''
    while True:
        size_meta = datar[beg:beg + META_SIZE]
        size_struct = datar[beg:beg + META_CHUNK]
        if len(size_struct) == 0:
            break
        size_data = struct.unpack('<I', size_struct)[0]
        chunk = datar[beg + META_SIZE:beg + size_data + META_SIZE]
        beg += size_data + META_SIZE
        datau += fkey.decrypt(chunk)

    # Now we have compressed data
    dataf2 = os.path.join(random_path, 'test%s.zstd'%random_name)
    with open(dataf2, "wb") as out:
        out.write(datau)
    with pyzstd.open(dataf2, "rb") as ff:
        datar = ff.read()

    # Now we have tar data
    dataf3 = os.path.join(random_path, 'test%s.tar'%random_name)
    with open(dataf3, "wb") as out:
        out.write(datar)

    with tarfile.open(dataf3, "r") as ff:
        ff.extract('file1%s.dat'%random_name, path=random_path)

    with open(os.path.join(random_path, 'file1%s.dat'%random_name), "rb") as ff:
        data1 = ff.read()
    assert data == data1

    with TarZstdFernetFile(dataf, "rb", fernet_key=key) as ff:
        ff.extract('file1%s.dat'%random_name, path=random_path)

    with open(os.path.join(random_path, 'file1%s.dat'%random_name), "rb") as ff:
        data1 = ff.read()
    assert data == data1

def test_store_info(random_path, random_name):
    sinfo = CofferInfo('titi', store_path=random_path)
    assert repr(sinfo).startswith('<Coffer')
    assert sinfo.mtime is None

def test_store_open(random_path, random_name):
    key = Fernet.generate_key()
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with store_open(dataf, mode='wb', container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
        assert repr(ff).startswith('<Coffer')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert not ff.readable

    with store_open(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    with open(dataf, "rb") as fdata:
        with store_open(fdata, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
            assert data == ff.read('file1%s.data'%random_name)
            assert data2 == ff.read('file2%s.data'%random_name)
            assert not ff.writable
            assert ff.readable

def test_store_basic(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG, logger="pycoffer")
    key = Fernet.generate_key()
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
        assert repr(ff).startswith('<Coffer')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert not ff.readable

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    data3 = randbytes(6589)
    with Coffer(dataf, "ab", container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        mtime2 = ff.mtime
        assert mtime2 > mtime

    with Coffer(dataf, "r", container_class=TarZstdFernetFile,
            container_params={'fernet_key':key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)

    with Coffer(dataf, "ab", container_class=TarZstdFernetFile,
            container_params={'fernet_key':key}) as ff:
        ff.delete('file3%s.data'%random_name)
        ff.append(data2a, 'file2%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile,
            container_params={'fernet_key':key}) as ff:
        with pytest.raises(OSError):
            data = ff.read('file3%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile,
            container_params={'fernet_key':key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 + data2a == ff.read('file2%s.data'%random_name)

    data4 = randbytes(54128)
    with Coffer(dataf, "ab", container_class=TarZstdFernetFile,
            container_params={'fernet_key':key}) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        ff.write(data4, '4/file%s.data'%random_name)

    dataf2 = os.path.join(random_path, 'file2%s.out'%random_name)
    with open(dataf2, "wb") as out:
        out.write(os.urandom(127 * 50))
    with open(dataf2, "rb") as ff:
        ddataf2 = ff.read()

    with Coffer(dataf, "ab", container_class=TarZstdFernetFile,
            container_params={'fernet_key':key}) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is False

    fff = None
    with Coffer(dataf, "rb", container_class=TarZstdFernetFile,
            container_params={'fernet_key':key}) as ff:
        fff = ff
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 + data2a == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert data4 == ff.read('4/file%s.data'%random_name)
    assert fff.closed is True

    with pytest.raises(OSError):
        with Coffer(dataf, "xb", container_class=TarZstdFernetFile,
                container_params={'fernet_key':key}) as ff:
            ff.write(data3, 'file3%s.data'%random_name)
            assert ff.closed is False

    with Coffer(dataf, "ab", container_class=TarZstdFernetFile,
            container_params={'fernet_key':key}) as ff:
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

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile,
            container_params={'fernet_key':key}) as ff:
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

    with Coffer(dataf, "ab", container_class=TarZstdFernetFile,
            container_params={'fernet_key':key}) as ff:
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

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile,
            container_params={'fernet_key':key}) as ff:
        edir = os.path.join(random_path, 'extract2%s'%random_name)
        os.makedirs(edir)
        ff.extract('test2/test/file222%s.data'%(random_name), edir)
        with pytest.raises(FileNotFoundError):
            ff.read(edir+'/test2/file222%s.data'%(random_name))
        with open(edir+'/test2/test/file222%s.data'%(random_name), "rb") as fff:
            assert ddataf2 == fff.read()

def test_store_no_flush(random_path, random_name):
    key = Fernet.generate_key()
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
        assert ff.modified is False
        ff.write(data, 'file1%s.data'%random_name)
        assert ff.modified is True
        ff.write(data2, 'file2%s.data'%random_name)
        assert ff.writable
        assert not ff.readable

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
        assert ff.modified is False
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable
        mtime = ff.mtime

    data3 = randbytes(6589)
    with Coffer(dataf, "ab", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False,
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

    with Coffer(dataf, "r", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
        assert ff.modified is False
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert ff.modified is False

    with Coffer(dataf, "ab", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
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

    with Coffer(dataf, "ab", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is True

    with pytest.raises(FileExistsError):
        with Coffer(dataf, "ab", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
            ff.add(dataf2, '5/file%s.data'%random_name, replace=False)

    with Coffer(dataf, "ab", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is True

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
        with pytest.raises(OSError):
            data = ff.read('file3%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 + data2a == ff.read('file2%s.data'%random_name)

    data4 = randbytes(54128)
    with Coffer(dataf, "ab", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        ff.write(data4, '4/file%s.data'%random_name)

    fff = None
    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
        fff = ff
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 + data2a == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert data4 == ff.read('4/file%s.data'%random_name)
    assert fff.closed is True

    with pytest.raises(OSError):
        with Coffer(dataf, "xb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}, auto_flush=False) as ff:
            ff.write(data3, 'file3%s.data'%random_name)
            assert ff.closed is False

def test_store_exception(random_path, random_name):
    key = Fernet.generate_key()
    data = randbytes(2487)
    data2 = randbytes(1536)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
        ff.write(data, 'file1%s.data'%random_name)
        with pytest.raises(FileNotFoundError):
            ff.add('badfile', 'file2%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        with pytest.raises(FileNotFoundError):
            assert data2 == ff.read('file2%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':None}) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(None, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(OSError):
        with Coffer('notafile.bad', "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
            assert ff.mtime is None
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(dataf, "rt", container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(dataf, "zz", container_params={'fernet_key':key}) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(dataf, None, container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with Coffer(dataf, 'rb', container_class=TarZstdFernetFile, container_params=None) as ff:
            assert data == ff.read('file1%s.data'%random_name)

def test_store_strings(random_path, random_name):
    key = Fernet.generate_key()
    length = 684
    data = [
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
    ]
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
        ff.writelines(data, 'file1%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key}) as ff:
        assert data == ff.readlines('file1%s.data'%random_name)

def test_store_secure_basic(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG)
    key = Fernet.generate_key()
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        assert repr(ff).startswith('<Coffer')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert not ff.readable

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    data3 = randbytes(6589)
    with Coffer(dataf, "ab", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        mtime2 = ff.mtime

    assert mtime2 > mtime

    with Coffer(dataf, "r", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)

    with Coffer(dataf, "ab", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        ff.delete('file3%s.data'%random_name)
        ff.append(data2a, 'file2%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        with pytest.raises(OSError):
            data = ff.read('file3%s.data'%random_name)

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 + data2a == ff.read('file2%s.data'%random_name)

    data4 = randbytes(54128)
    with Coffer(dataf, "ab", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        ff.write(data4, '4/file%s.data'%random_name)

    dataf2 = os.path.join(random_path, 'file2%s.out'%random_name)
    with open(dataf2, "wb") as out:
        out.write(os.urandom(127 * 50))
    with open(dataf2, "rb") as ff:
        ddataf2 = ff.read()

    with Coffer(dataf, "ab", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is False

    fff = None
    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        fff = ff
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 + data2a == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert data4 == ff.read('4/file%s.data'%random_name)
    assert fff.closed is True

    with pytest.raises(OSError):
        with Coffer(dataf, "xb", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
                secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
            ff.write(data3, 'file3%s.data'%random_name)
            assert ff.closed is False

    extdir = os.path.join(random_path, 'extract_tar%s'%random_name)
    os.makedirs(extdir, exist_ok=True)
    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        ff.extractall(extdir)

    extdir = os.path.join(random_path, 'extract_tar2%s'%random_name)
    os.makedirs(extdir, exist_ok=True)
    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        ff.extract('file3%s.data'%random_name, extdir)

def test_store_secure_tmp(random_path, random_name):
    key = Fernet.generate_key()
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='wb', container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        assert repr(ff).startswith('<Coffer')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert not ff.readable

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    with Coffer(dataf, "rb", container_class=TarZstdFernetFile, container_params={'fernet_key':key},
            secure_open=zstd_open, secure_params={'fernet_key': key}) as ff:
        for member in ff.getmembers():
            with zstd_open(member.path, 'rb', fernet_key=key) as fff:
                datar = fff.read()
                if member.name == 'file1%s.data'%random_name:
                    assert data == datar
                elif member.name == 'file2%s.data'%random_name:
                    assert data2 == datar
            with pytest.raises(ValueError):
                with zstd_open(member.path, 'rb', fernet_key=None) as fff:
                    assert fff.read() is not None

