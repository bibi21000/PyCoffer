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

from filelock import Timeout as filelockTimeout

import cofferfile
from cofferfile import META_CHUNK, META_SIZE
from pycoffer import CofferInfo
from pycoffer.coffers.null import CofferNull, open as store_open
from pyzstd import open as zstd_open
from cofferfile.zstd import clean_level_or_option, ZstdTarFile

import pytest


def test_null_open(random_path, random_name):
    data = randbytes(586)
    data2 = randbytes(1536)
    data2a = randbytes(1287)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with store_open(dataf, mode='wb') as ff:
        assert repr(ff).startswith('<CofferNull')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert ff.readable

    with store_open(dataf, "rb") as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    with open(dataf, "rb") as fdata:
        with store_open(fdata, "rb") as ff:
            assert data == ff.read('file1%s.data'%random_name)
            assert data2 == ff.read('file2%s.data'%random_name)
            assert not ff.writable
            assert ff.readable

def test_null_basic(random_path, random_name):
    data = randbytes(125)
    data2 = randbytes(875)
    data2a = randbytes(2156)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with CofferNull(dataf, mode='wb') as ff:
        assert repr(ff).startswith('<CofferNull')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert ff.readable

    with CofferNull(dataf, "rb") as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

    data3 = randbytes(6589)
    with CofferNull(dataf, "ab") as ff:
        ff.write(data3, 'file3%s.data'%random_name)
        mtime2 = ff.mtime

    with CofferNull(dataf, "r") as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert data3 == ff.read('file3%s.data'%random_name)

    with CofferNull(dataf, "ab") as ff:
        ff.delete('file3%s.data'%random_name)
        ff.append(data2a, 'file2%s.data'%random_name)

    with CofferNull(dataf, "rb") as ff:
        with pytest.raises(OSError):
            data = ff.read('file3%s.data'%random_name)

    assert CofferNull.gen_params() is not None

def test_null_exception(random_path, random_name):
    data = randbytes(125)
    data2 = randbytes(896)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with pytest.raises(ValueError):
        with CofferNull(dataf, "rt") as ff:
            ff.read(data, 'file1%s.data'%random_name)

    with pytest.raises(TypeError):
        with CofferNull(1, "r") as ff:
            ff.read(data, 'file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with CofferNull(dataf, None) as ff:
            ff.read(data, 'file1%s.data'%random_name)

    with pytest.raises(ValueError):
        with store_open(dataf, "rt") as ff:
            ff.read(data, 'file1%s.data'%random_name)

    with pytest.raises(TypeError):
        with store_open(1, "r") as ff:
            ff.read(data, 'file1%s.data'%random_name)

    with pytest.raises(TypeError):
        with store_open(dataf, None) as ff:
            ff.read(data, 'file1%s.data'%random_name)

