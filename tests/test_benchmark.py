# -*- encoding: utf-8 -*-
"""Test module

"""
import os
import importlib
import time
from random import randbytes
import urllib.request
import zipfile
import tarfile
import logging

# ~ from cryptography.fernet import Fernet
from nacl import utils
from nacl.secret import SecretBox
from Crypto.Random import get_random_bytes

import pyzstd

import fernetfile

import pytest
from fernetfile.zstd import FernetFile as _ZstdFernetFile, CParameter, open as zstd_open
import naclfile
from naclfile import NaclFile
from naclfile.zstd import NaclFile as _ZstdNaclFile, open as naclz_open
from naclfile.tar import TarFile as _TarZstdNaclFile
from aesfile import AesFile
from aesfile.zstd import AesFile as _ZstdAesFile, open as aesz_open
from aesfile.tar import TarFile as _TarZstdAesFile
from fernetfile.tar import TarFile as _TarZstdFernetFile
from pycoffer import Coffer
from pycoffer.store import CofferStore
from pycoffer.bank import CofferBank
from pycoffer.market import CofferMarket

class ZstdFernetFile(_ZstdFernetFile):
    pass
class TarZstdFernetFile(_TarZstdFernetFile):
    pass

class ZstdNaclFile(_ZstdNaclFile):
    pass
class TarZstdNaclFile(_TarZstdNaclFile):
    pass

class ZstdAesFile(_ZstdAesFile):
    pass
class TarZstdAesFile(_TarZstdAesFile):
    pass

try:
    import pytest_ordering
    DO = True
    # ~ DO = False
except ModuleNotFoundError:
    DO = False

@pytest.mark.skipif(not DO, reason="requires the pytest_ordering package")
@pytest.mark.run(order=0)
def test_benchmark_fstore_header(random_path):
    with open('BENCHMARK.md','wt') as ff:
        ff.write("# Benchmarks Coffer\n")
        ff.write("\n")
        ff.write("Tests done with autoflush, with or without open_secure.\n")
        ff.write("\n")
        ff.write("WT -1, ... are the last store.add time in store\n")
        ff.write("\n")
        ff.write("WTime is the total write time (WT -1 + WT -2 + WT -3 + ...).\n")
        ff.write("\n")
        ff.write("Extime the time spent to extract all files from coffer\n")
        ff.write("\n")
        ff.write("| Class             | Data              | NbDocs | Orig size | Crypt size | C Ratio | WTime  | Extime | WT -1 | WT -2 | WT -3 | WT -4 |\n")
        ff.write("|:------------------|:------------------|-------:|----------:|-----------:|--------:|-------:|-------:|------:|------:|------:|------:|\n")
    if os.path.isfile('docpython.pdf.zip') is False:
        urllib.request.urlretrieve("https://docs.python.org/3/archives/python-3.13-docs-pdf-a4.zip", "docpython.pdf.zip")
        with zipfile.ZipFile('docpython.pdf.zip', 'r') as zip_ref:
            zip_ref.extractall('.')
    if os.path.isfile('docpython.html.zip') is False:
        urllib.request.urlretrieve("https://docs.python.org/3/archives/python-3.13-docs-html.zip", "docpython.html.zip")
        with zipfile.ZipFile('docpython.html.zip', 'r') as zip_ref:
            zip_ref.extractall('.')

@pytest.mark.skipif(not DO, reason="requires the pytest_ordering package")
@pytest.mark.run(order=1)
@pytest.mark.parametrize("dt, cls, container_params, secure_params, nb_doc", [
    ('genindex-all.html', CofferBank, {'coffer_key':get_random_bytes(16)}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('genindex-all.html', CofferStore, {'coffer_key':utils.random(SecretBox.KEY_SIZE)}, {}, 5),
    ('genindex-all.html', CofferMarket, {}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('searchindex.js', CofferBank, {'coffer_key':get_random_bytes(16)}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('searchindex.js', CofferStore, {'coffer_key':utils.random(SecretBox.KEY_SIZE)}, {}, 5),
    ('searchindex.js', CofferMarket, {}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('library.pdf', CofferBank, {'coffer_key':get_random_bytes(16)}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('library.pdf', CofferStore, {'coffer_key':utils.random(SecretBox.KEY_SIZE)}, {}, 5),
    ('library.pdf', CofferMarket, {}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('mixed', CofferBank, {'coffer_key':get_random_bytes(16)}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('mixed', CofferStore, {'coffer_key':utils.random(SecretBox.KEY_SIZE)}, {}, 5),
    ('mixed', CofferMarket, {}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 5),

    ('genindex-all.html', CofferBank, {'coffer_key':get_random_bytes(16)}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 25),
    ('genindex-all.html', CofferStore, {'coffer_key':utils.random(SecretBox.KEY_SIZE)}, {}, 25),
    ('genindex-all.html', CofferMarket, {}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 25),
    ('searchindex.js', CofferBank, {'coffer_key':get_random_bytes(16)}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 25),
    ('searchindex.js', CofferStore, {'coffer_key':utils.random(SecretBox.KEY_SIZE)}, {}, 25),
    ('searchindex.js', CofferMarket, {}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 25),
    ('library.pdf', CofferBank, {'coffer_key':get_random_bytes(16)}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 25),
    ('library.pdf', CofferStore, {'coffer_key':utils.random(SecretBox.KEY_SIZE)}, {}, 25),
    ('library.pdf', CofferMarket, {}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 25),
    ('mixed', CofferBank, {'coffer_key':get_random_bytes(16)}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 25),
    ('mixed', CofferStore, {'coffer_key':utils.random(SecretBox.KEY_SIZE)}, {}, 25),
    ('mixed', CofferMarket, {}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 25),
])
def test_benchmark_fstore(caplog, random_path, dt, cls, container_params, secure_params, nb_doc):
    caplog.set_level(logging.DEBUG)
    dataf = os.path.join(random_path, 'test.frnt')
    time_start = time.time()
    times = []
    file_size = 0
    with cls(dataf, mode='w',**container_params, **secure_params) as ff:
        for i in range(nb_doc):
            if dt in ['download.html', 'genindex-all.html', 'searchindex.js']:
                df = os.path.join('python-3.13-docs-html', dt)
                ff.add(df, dt + '%s'%i)
                file_size += os.path.getsize(df)
            elif dt in ['library.pdf', 'using.pdf']:
                df = os.path.join('docs-pdf', dt)
                ff.add(df, dt + '%s'%i)
                file_size += os.path.getsize(df)
            elif 'mixed' in dt :
                for ddt in ['download.html', 'genindex-all.html', 'searchindex.js', 'library.pdf', 'using.pdf']:
                    if ddt in ['download.html', 'genindex-all.html', 'searchindex.js']:
                        df = os.path.join('python-3.13-docs-html', ddt)
                        ff.add(df, ddt + '%s'%i)
                        file_size += os.path.getsize(df)
                    elif ddt in ['library.pdf', 'using.pdf']:
                        df = os.path.join('docs-pdf', ddt)
                        ff.add(df, ddt + '%s'%i)
                        file_size += os.path.getsize(df)
            times.append(time.time())
    time_write = time.time()
    with cls(dataf, "rb", **container_params, **secure_params) as ff:
        ff.extractall('extract_tar_%s'%random_path)
    time_read = time.time()
    # ~ assert data == datar
    comp_size = os.path.getsize(dataf)
    for i in range(nb_doc):
        if dt in ['download.html', 'genindex-all.html', 'searchindex.js']:
            with open(os.path.join('python-3.13-docs-html', dt),'rb') as ff:
                data = ff.read()
            with open(os.path.join('extract_tar_%s'%random_path, dt + '%s'%i),'rb') as ff:
                datar = ff.read()
            assert data == datar
        elif dt in ['library.pdf', 'using.pdf']:
            with open(os.path.join('docs-pdf', dt),'rb') as ff:
                data = ff.read()
            with open(os.path.join('extract_tar_%s'%random_path, dt + '%s'%i),'rb') as ff:
                datar = ff.read()
            assert data == datar
        elif 'mixed' in dt :
            for ddt in ['download.html', 'genindex-all.html', 'searchindex.js', 'library.pdf', 'using.pdf']:
                if ddt in ['download.html', 'genindex-all.html', 'searchindex.js']:
                    with open(os.path.join('python-3.13-docs-html', ddt),'rb') as ff:
                        data = ff.read()
                    with open(os.path.join('extract_tar_%s'%random_path, ddt + '%s'%i),'rb') as ff:
                        datar = ff.read()
                    assert data == datar
                elif ddt in ['library.pdf', 'using.pdf']:
                    with open(os.path.join('docs-pdf', ddt),'rb') as ff:
                        data = ff.read()
                    with open(os.path.join('extract_tar_%s'%random_path, ddt + '%s'%i),'rb') as ff:
                        datar = ff.read()
                    assert data == datar

    with open('BENCHMARK.md','at') as ff:
        ff.write("|%-18s |%-18s | %6.0f | %9.0f |  %9.0f | %7.2f | %6.2f | %6.2f | %5.2f | %5.2f | %5.2f | %5.2f |\n" %
        (("%s" % cls).split('.')[-1][:-2], dt, nb_doc, file_size / 1024, comp_size / 1024, comp_size / file_size * 100,
        time_write - time_start, time_read - time_write, times[-1] - times[-2], times[-2] - times[-3], times[-3] - times[-4], times[-4] - times[-5]))

@pytest.mark.skipif(not DO, reason="requires the pytest_ordering package")
@pytest.mark.run(order=10)
def test_benchmark_fstore_header_tmp(random_path):
    with open('BENCHMARK.md','at') as ff:
        ff.write("# Benchmarks Coffer with cache in tmpfs\n")
        ff.write("\n")
        ff.write("mount -t tmpfs tmpfs /tmp/coffertmp/ -o size=4g\n")
        ff.write("\n")
        ff.write("| Class             | Data              | NbDocs | Orig size | Crypt size | C Ratio | WTime  | Extime | WT -1 | WT -2 | WT -3 | WT -4 |\n")
        ff.write("|:------------------|:------------------|-------:|----------:|-----------:|--------:|-------:|-------:|------:|------:|------:|------:|\n")
    if os.path.isfile('docpython.pdf.zip') is False:
        urllib.request.urlretrieve("https://docs.python.org/3/archives/python-3.13-docs-pdf-a4.zip", "docpython.pdf.zip")
        with zipfile.ZipFile('docpython.pdf.zip', 'r') as zip_ref:
            zip_ref.extractall('.')
    if os.path.isfile('docpython.html.zip') is False:
        urllib.request.urlretrieve("https://docs.python.org/3/archives/python-3.13-docs-html.zip", "docpython.html.zip")
        with zipfile.ZipFile('docpython.html.zip', 'r') as zip_ref:
            zip_ref.extractall('.')

@pytest.mark.skipif(not DO, reason="requires the pytest_ordering package")
@pytest.mark.run(order=11)
@pytest.mark.parametrize("dt, cls, container_params, secure_params, nb_doc", [
    ('mixed', CofferBank, {'coffer_key':get_random_bytes(16)}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 25),
    ('mixed', CofferStore, {'coffer_key':utils.random(SecretBox.KEY_SIZE)}, {}, 25),
    ('mixed', CofferMarket, {}, {'secure_key':utils.random(SecretBox.KEY_SIZE)}, 25),
])
def test_benchmark_fstore_tmp(caplog, random_path, dt, cls, container_params, secure_params, nb_doc):
    caplog.set_level(logging.DEBUG)
    dataf = os.path.join(random_path, 'test.frnt')
    time_start = time.time()
    times = []
    file_size = 0
    with cls(dataf, mode='w',**container_params, **secure_params, temp_dir='/tmp/coffertmp') as ff:
        for i in range(nb_doc):
            if dt in ['download.html', 'genindex-all.html', 'searchindex.js']:
                df = os.path.join('python-3.13-docs-html', dt)
                ff.add(df, dt + '%s'%i)
                file_size += os.path.getsize(df)
            elif dt in ['library.pdf', 'using.pdf']:
                df = os.path.join('docs-pdf', dt)
                ff.add(df, dt + '%s'%i)
                file_size += os.path.getsize(df)
            elif 'mixed' in dt :
                for ddt in ['download.html', 'genindex-all.html', 'searchindex.js', 'library.pdf', 'using.pdf']:
                    if ddt in ['download.html', 'genindex-all.html', 'searchindex.js']:
                        df = os.path.join('python-3.13-docs-html', ddt)
                        ff.add(df, ddt + '%s'%i)
                        file_size += os.path.getsize(df)
                    elif ddt in ['library.pdf', 'using.pdf']:
                        df = os.path.join('docs-pdf', ddt)
                        ff.add(df, ddt + '%s'%i)
                        file_size += os.path.getsize(df)
            times.append(time.time())
    time_write = time.time()
    with cls(dataf, "rb", **container_params, **secure_params, temp_dir='/tmp/coffertmp') as ff:
        ff.extractall('extract_tar_%s'%random_path)
    time_read = time.time()
    # ~ assert data == datar
    comp_size = os.path.getsize(dataf)
    for i in range(nb_doc):
        if dt in ['download.html', 'genindex-all.html', 'searchindex.js']:
            with open(os.path.join('python-3.13-docs-html', dt),'rb') as ff:
                data = ff.read()
            with open(os.path.join('extract_tar_%s'%random_path, dt + '%s'%i),'rb') as ff:
                datar = ff.read()
            assert data == datar
        elif dt in ['library.pdf', 'using.pdf']:
            with open(os.path.join('docs-pdf', dt),'rb') as ff:
                data = ff.read()
            with open(os.path.join('extract_tar_%s'%random_path, dt + '%s'%i),'rb') as ff:
                datar = ff.read()
            assert data == datar
        elif 'mixed' in dt :
            for ddt in ['download.html', 'genindex-all.html', 'searchindex.js', 'library.pdf', 'using.pdf']:
                if ddt in ['download.html', 'genindex-all.html', 'searchindex.js']:
                    with open(os.path.join('python-3.13-docs-html', ddt),'rb') as ff:
                        data = ff.read()
                    with open(os.path.join('extract_tar_%s'%random_path, ddt + '%s'%i),'rb') as ff:
                        datar = ff.read()
                    assert data == datar
                elif ddt in ['library.pdf', 'using.pdf']:
                    with open(os.path.join('docs-pdf', ddt),'rb') as ff:
                        data = ff.read()
                    with open(os.path.join('extract_tar_%s'%random_path, ddt + '%s'%i),'rb') as ff:
                        datar = ff.read()
                    assert data == datar

    with open('BENCHMARK.md','at') as ff:
        ff.write("|%-18s |%-18s | %6.0f | %9.0f |  %9.0f | %7.2f | %6.2f | %6.2f | %5.2f | %5.2f | %5.2f | %5.2f |\n" %
        (("%s" % cls).split('.')[-1][:-2], dt, nb_doc, file_size / 1024, comp_size / 1024, comp_size / file_size * 100,
        time_write - time_start, time_read - time_write, times[-1] - times[-2], times[-2] - times[-3], times[-3] - times[-4], times[-4] - times[-5]))
