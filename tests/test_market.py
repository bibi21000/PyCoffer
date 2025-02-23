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

from nacl import utils
from nacl.secret import SecretBox
from filelock import Timeout as filelockTimeout

import cofferfile
from cofferfile import META_CHUNK, META_SIZE
from pycoffer import CofferInfo
from pycoffer.coffers.market import CofferMarket, open as store_open
from pyzstd import open as zstd_open
from naclfile.tar import TarFile as TarZstdNaclFile
from cofferfile.zstd import clean_level_or_option, ZstdTarFile

import pytest


def test_market_open(random_path, random_name):
    secure_key = utils.random(SecretBox.KEY_SIZE)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with store_open(dataf, mode='wb', secure_key=secure_key) as ff:
        assert repr(ff).startswith('<CofferMarket')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert ff.readable

    with store_open(dataf, "rb", secure_key=secure_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    with open(dataf, "rb") as fdata:
        with store_open(fdata, "rb", secure_key=secure_key) as ff:
            assert data == ff.read('file1%s.data'%random_name)
            assert data2 == ff.read('file2%s.data'%random_name)
            assert not ff.writable
            assert ff.readable

def test_market_basic(random_path, random_name):
    secure_key = utils.random(SecretBox.KEY_SIZE)
    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with CofferMarket(dataf, mode='wb', secure_key=secure_key) as ff:
        assert repr(ff).startswith('<CofferMarket')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert ff.readable

    with CofferMarket(dataf, "rb", secure_key=secure_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    data3 = randbytes(6589)
    with CofferMarket(dataf, "ab", secure_key=secure_key) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        mtime2 = ff.mtime

    with CofferMarket(dataf, "r", secure_key=secure_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)

    with CofferMarket(dataf, "ab", secure_key=secure_key) as ff:
        ff.delete('file3%s.data'%random_name)
        ff.append(data2a, 'file2%s.data'%random_name)

    with CofferMarket(dataf, "rb", secure_key=secure_key) as ff:
        with pytest.raises(OSError):
            data = ff.read('file3%s.data'%random_name)

    with CofferMarket(dataf, "rb", secure_key=secure_key) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 + data2a == ff.read('file2%s.data'%random_name)

    data4 = randbytes(54128)
    with CofferMarket(dataf, "ab", secure_key=secure_key) as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        ff.write(data4, '4/file%s.data'%random_name)

    dataf2 = os.path.join(random_path, 'file2%s.out'%random_name)
    with open(dataf2, "wb") as out:
        out.write(os.urandom(127 * 50))
    with open(dataf2, "rb") as ff:
        ddataf2 = ff.read()

    with CofferMarket(dataf, "ab", secure_key=secure_key) as ff:
        assert ff.modified is False
        ff.add(dataf2, '5/file%s.data'%random_name)
        assert ff.modified is True

    fff = None
    with CofferMarket(dataf, "rb", secure_key=secure_key) as ff:
        fff = ff
        assert data == ff.read('file1%s.data'%random_name)
        assert ff.modified is False
        assert data2 + data2a == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)
        assert data4 == ff.read('4/file%s.data'%random_name)
    assert fff.closed is True

    with pytest.raises(OSError):
        with CofferMarket(dataf, "xb", secure_key=secure_key) as ff:
            ff.write(data3, 'file3%s.data'%random_name)
            assert ff.closed is False

    assert CofferMarket.gen_params() is not None

def test_market_exception(random_path, random_name):
    secure_key = utils.random(SecretBox.KEY_SIZE)
    data = randbytes(2487)
    data2 = randbytes(1536)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with pytest.raises(ValueError):
        with CofferMarket(dataf, "rt", secure_key=secure_key) as ff:
            ff.read(data, 'file1%s.data'%random_name)

    with pytest.raises(TypeError):
        with CofferMarket(1, "r", secure_key=secure_key) as ff:
            ff.read(data, 'file1%s.data'%random_name)

    with pytest.raises(TypeError):
        with CofferMarket(dataf, None, secure_key=secure_key) as ff:
            ff.read(data, 'file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with store_open(dataf, "rt", secure_key=secure_key) as ff:
            ff.read(data, 'file1%s.data'%random_name)

    with pytest.raises(TypeError):
        with store_open(1, "r", secure_key=secure_key) as ff:
            ff.read(data, 'file1%s.data'%random_name)

    with pytest.raises(TypeError):
        with store_open(dataf, None, secure_key=secure_key) as ff:
            ff.read(data, 'file1%s.data'%random_name)

def test_market_crypt_open(random_path, random_name):
    secure_key = utils.random(SecretBox.KEY_SIZE)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    dataf2 = os.path.join(random_path, 'copy%s.out'%random_name)
    with open(dataf2, "wb") as out:
        out.write(os.urandom(589))
    with open(dataf2, "rb") as ff:
        data = ff.read()

    with CofferMarket(dataf, "ab", secure_key=secure_key) as ff:
        with open(dataf2, "rb") as fff, ff.crypt_open(dataf2+'.crypt', 'wb') as ggg:
            ggg.write(fff.read())

    with open(dataf2+'.crypt', "rb") as ff:
        assert data != ff.read()

    with CofferMarket(dataf, "rb", secure_key=secure_key) as ff:
        with open(dataf2+'.uncrypt', "wb") as fff, ff.crypt_open(dataf2+'.crypt', 'rb') as ggg:
            fff.write(ggg.read())

    with open(dataf2+'.uncrypt', "rb") as ff:
        assert data == ff.read()
