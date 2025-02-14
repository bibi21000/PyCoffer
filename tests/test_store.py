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
from nacl import utils
from nacl.secret import SecretBox
from filelock import Timeout as filelockTimeout

import cofferfile
from cofferfile import META_CHUNK, META_SIZE
from pycoffer import CofferInfo
from pycoffer.store import CofferStore, open as store_open
from naclfile.zstd import open as zstd_open
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
    assert repr(sinfo).startswith('<CofferInfo')
    assert sinfo.mtime is None

def test_store_open(random_path, random_name):
    key = Fernet.generate_key()
    secret_key = utils.random(SecretBox.KEY_SIZE)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with store_open(dataf, mode='wb', fernet_key=key, secret_key=secret_key) as ff:
        assert repr(ff).startswith('<CofferStore')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert not ff.readable

    with store_open(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    with open(dataf, "rb") as fdata:
        with store_open(fdata, "rb", fernet_key=key, secret_key=secret_key) as ff:
            assert data == ff.read('file1%s.data'%random_name)
            assert data2 == ff.read('file2%s.data'%random_name)
            assert not ff.writable
            assert ff.readable

def test_store_basic(random_path, random_name):
    key = Fernet.generate_key()
    secret_key = utils.random(SecretBox.KEY_SIZE)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with CofferStore(dataf, mode='wb', fernet_key=key, secret_key=secret_key) as ff:
        assert repr(ff).startswith('<CofferStore')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert not ff.readable

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    data3 = randbytes(6589)
    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        mtime2 = ff.mtime

    assert mtime2 > mtime

    with CofferStore(dataf, "r", fernet_key=key, secret_key=secret_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)

    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key) as ff:
        ff.delete('file3%s.data'%random_name)
        ff.append(data2a, 'file2%s.data'%random_name)

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        with pytest.raises(OSError):
            data = ff.read('file3%s.data'%random_name)

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 + data2a == ff.read('file2%s.data'%random_name)

    data4 = randbytes(54128)
    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        ff.write(data4, '4/file%s.data'%random_name)

    dataf2 = os.path.join(random_path, 'file2%s.out'%random_name)
    with open(dataf2, "wb") as out:
        out.write(os.urandom(127 * 50))
    with open(dataf2, "rb") as ff:
        ddataf2 = ff.read()

    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is False

    fff = None
    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        fff = ff
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 + data2a == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert data4 == ff.read('4/file%s.data'%random_name)
    assert fff.closed is True

    with pytest.raises(OSError):
        with CofferStore(dataf, "xb", fernet_key=key, secret_key=secret_key) as ff:
            ff.write(data3, 'file3%s.data'%random_name)
            assert ff.closed is False

def test_store_no_flush(random_path, random_name):
    key = Fernet.generate_key()
    secret_key = utils.random(SecretBox.KEY_SIZE)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with CofferStore(dataf, mode='wb', fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
        assert ff.modified is False
        ff.write(data, 'file1%s.data'%random_name)
        assert ff.modified is True
        ff.write(data2, 'file2%s.data'%random_name)
        assert ff.writable
        assert not ff.readable

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
        assert ff.modified is False
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable
        mtime = ff.mtime

    data3 = randbytes(6589)
    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key, auto_flush=False,
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

    with CofferStore(dataf, "r", fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
        assert ff.modified is False
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert ff.modified is False

    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
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

    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is True

    with pytest.raises(FileExistsError):
        with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
            ff.add(dataf2, '5/file%s.data'%random_name, replace=False)

    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is True

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
        with pytest.raises(OSError):
            data = ff.read('file3%s.data'%random_name)

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 + data2a == ff.read('file2%s.data'%random_name)

    data4 = randbytes(54128)
    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        ff.write(data4, '4/file%s.data'%random_name)

    fff = None
    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
        fff = ff
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 + data2a == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert data4 == ff.read('4/file%s.data'%random_name)
    assert fff.closed is True

    with pytest.raises(OSError):
        with CofferStore(dataf, "xb", fernet_key=key, secret_key=secret_key, auto_flush=False) as ff:
            ff.write(data3, 'file3%s.data'%random_name)
            assert ff.closed is False

def test_store_exception(random_path, random_name):
    key = Fernet.generate_key()
    secret_key = utils.random(SecretBox.KEY_SIZE)
    data = randbytes(2487)
    data2 = randbytes(1536)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with CofferStore(dataf, mode='wb', fernet_key=key, secret_key=secret_key) as ff:
        ff.write(data, 'file1%s.data'%random_name)
        with pytest.raises(FileNotFoundError):
            ff.add('badfile', 'file2%s.data'%random_name)

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        with pytest.raises(filelockTimeout):
            with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
                assert data == ff.read('file1%s.data'%random_name)

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        with pytest.raises(FileNotFoundError):
            assert data2 == ff.read('file2%s.data'%random_name)

    with pytest.raises(ValueError):
        with CofferStore(dataf, "rb", fernet_key=None, secret_key=secret_key) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with CofferStore(None, "rb", fernet_key=key, secret_key=secret_key) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(OSError):
        with CofferStore('notafile.bad', "rb", fernet_key=key, secret_key=secret_key) as ff:
            assert ff.mtime is None
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with CofferStore(dataf, "rt", fernet_key=key, secret_key=secret_key) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with CofferStore(dataf, "zz", fernet_key=key, secret_key=secret_key) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with CofferStore(dataf, None, fernet_key=key, secret_key=secret_key) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with store_open(dataf, 'rt', fernet_key=key, secret_key=secret_key) as ff:
            assert data == ff.read('file1%s.data'%random_name)

    with pytest.raises(TypeError):
        with store_open(None, 'r', fernet_key=key, secret_key=secret_key) as ff:
            assert data == ff.read('file1%s.data'%random_name)

def test_store_strings(random_path, random_name):
    key = Fernet.generate_key()
    secret_key = utils.random(SecretBox.KEY_SIZE)
    length = 684
    data = [
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
        ''.join(choices(string.ascii_letters + string.digits, k=length)),
    ]
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with CofferStore(dataf, mode='wb', fernet_key=key, secret_key=secret_key) as ff:
        ff.writelines(data, 'file1%s.data'%random_name)

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        assert data == ff.readlines('file1%s.data'%random_name)

def test_store_secure_basic(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG, logger="pycoffer")

    key = Fernet.generate_key()
    secret_key = utils.random(SecretBox.KEY_SIZE)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with CofferStore(dataf, mode='wb', fernet_key=key, secret_key=secret_key) as ff:
        assert repr(ff).startswith('<CofferStore')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert not ff.readable

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    data3 = randbytes(6589)
    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        mtime2 = ff.mtime

    assert mtime2 > mtime

    with CofferStore(dataf, "r", fernet_key=key, secret_key=secret_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)

    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key) as ff:
        ff.delete('file3%s.data'%random_name)
        ff.append(data2a, 'file2%s.data'%random_name)

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        with pytest.raises(OSError):
            data = ff.read('file3%s.data'%random_name)

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 + data2a == ff.read('file2%s.data'%random_name)

    data4 = randbytes(54128)
    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        ff.write(data4, '4/file%s.data'%random_name)

    dataf2 = os.path.join(random_path, 'file2%s.out'%random_name)
    with open(dataf2, "wb") as out:
        out.write(os.urandom(127 * 50))
    with open(dataf2, "rb") as ff:
        ddataf2 = ff.read()

    with CofferStore(dataf, "ab", fernet_key=key, secret_key=secret_key) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is False

    fff = None
    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        fff = ff
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 + data2a == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert data4 == ff.read('4/file%s.data'%random_name)
    assert fff.closed is True

    with pytest.raises(OSError):
        with CofferStore(dataf, "xb", fernet_key=key, secret_key=secret_key) as ff:
            ff.write(data3, 'file3%s.data'%random_name)
            assert ff.closed is False

    extdir = os.path.join(random_path, 'extract_tar%s'%random_name)
    os.makedirs(extdir, exist_ok=True)
    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        ff.extractall(extdir)

def test_store_secure_tmp(random_path, random_name):
    key = Fernet.generate_key()
    secret_key = utils.random(SecretBox.KEY_SIZE)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with CofferStore(dataf, mode='wb', fernet_key=key, secret_key=secret_key) as ff:
        assert repr(ff).startswith('<CofferStore')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert not ff.readable

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    with CofferStore(dataf, "rb", fernet_key=key, secret_key=secret_key) as ff:
        for member in ff.getmembers():
            assert repr(member).startswith('<CofferInfo')
            assert member.mtime is not None
            with zstd_open(member.path, 'rb', secret_key=secret_key) as fff:
                datar = fff.read()
                if member.name == 'file1%s.data'%random_name:
                    assert data == datar
                elif member.name == 'file2%s.data'%random_name:
                    assert data2 == datar
            with pytest.raises(ValueError):
                with zstd_open(member.path, 'rb', secret_key=None) as fff:
                    assert fff.read() is not None

