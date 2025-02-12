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

from cryptography.fernet import Fernet
from nacl import utils
from nacl.secret import SecretBox

import fernetfile

import pytest
from fernetfile.zstd import FernetFile as _ZstdFernetFile, CParameter, open as zstd_open
import naclfile
from naclfile import NaclFile
from naclfile.zstd import NaclFile as _ZstdNaclFile, open as naclz_open
from naclfile.tar import TarFile as _TarZstdNaclFile
from cofferfile.aes import AesFile
from fernetfile.tar import TarFile as _TarZstdFernetFile
from pycoffer.store import CofferStore
from .test_chain import Bz2FernetFile, LzmaFernetFile, TarBz2FernetFile, TarLzmaFernetFile

class ZstdFernetFile(_ZstdFernetFile):
    pass

class ZstdNaclFile(_ZstdNaclFile):
    pass

class TarZstdNaclFile(_TarZstdNaclFile):
    pass

class TarZstdFernetFile(_TarZstdFernetFile):
    pass

try:
    import pytest_ordering
    # ~ DO = True
    DO = False
except ModuleNotFoundError:
    DO = False


@pytest.mark.skipif(not DO, reason="requires the pytest_ordering package")
@pytest.mark.run(order=0)
def test_benchmark_fstore_header(random_path):
    with open('BENCHMARK.md','wt') as ff:
        ff.write("# Benchmarks CofferStore\n")
        ff.write("\n")
        ff.write("Tests done with autoflush, with or without open_secure.\n")
        ff.write("\n")
        ff.write("WT -1, ... are the last store.add time in store\n")
        ff.write("\n")
        ff.write("WTime is the total write time. RTime the time spent to read\n")
        ff.write("\n")
        ff.write("| Data              | NbDocs | Op sec | Orig size | Crypt size | C Ratio | WTime | Rtime | WT -1 | WT -2 | WT -3 | WT -4 |\n")
        ff.write("|:------------------|-------:|-------:|----------:|-----------:|--------:|------:|------:|------:|------:|------:|------:|\n")
    if os.path.isfile('docpython.pdf.zip') is False:
        urllib.request.urlretrieve("https://docs.python.org/3/archives/python-3.13-docs-pdf-a4.zip", "docpython.pdf.zip")
        with zipfile.ZipFile('docpython.pdf.zip', 'r') as zip_ref:
            zip_ref.extractall('.')
    if os.path.isfile('docpython.html.zip') is False:
        urllib.request.urlretrieve("https://docs.python.org/3/archives/python-3.13-docs-html.zip", "docpython.html.zip")
        with zipfile.ZipFile('docpython.html.zip', 'r') as zip_ref:
            zip_ref.extractall('.')


# ~ @pytest.mark.skip("Manual test")
@pytest.mark.skipif(not DO, reason="requires the pytest_ordering package")
@pytest.mark.run(order=1)
@pytest.mark.parametrize("dt, cls, key, secure_open, secure_params, nb_doc", [
    ('genindex-all.html', TarZstdFernetFile, {Fernet.generate_key()}, None, None, 5),
    ('genindex-all.html', TarZstdFernetFile, {Fernet.generate_key()}, zstd_open, {'fernet_key':Fernet.generate_key()}, 5),
    ('genindex-all.html', TarZstdFernetFile, {Fernet.generate_key()}, fernetfile.open, {'fernet_key':Fernet.generate_key()}, 5),
    ('genindex-all.html', TarZstdFernetFile, {Fernet.generate_key()}, naclz_open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('genindex-all.html', TarZstdFernetFile, {Fernet.generate_key()}, naclfile.open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('genindex-all.html', TarZstdFernetFile, {Fernet.generate_key()}, None, None, 20),
    ('genindex-all.html', TarZstdFernetFile, {Fernet.generate_key()}, zstd_open, {'fernet_key':{Fernet.generate_key()}}, 20),
    ('genindex-all.html', TarZstdFernetFile, {Fernet.generate_key()}, fernetfile.open, {'fernet_key':{Fernet.generate_key()}}, 20),
    ('genindex-all.html', TarZstdFernetFile, {Fernet.generate_key()}, naclz_open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 20),
    ('genindex-all.html', TarZstdFernetFile, {Fernet.generate_key()}, naclfile.open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 20),
    ('searchindex.js', TarZstdFernetFile, {Fernet.generate_key()}, None, None, 5),
    ('searchindex.js', TarZstdFernetFile, {Fernet.generate_key()}, zstd_open, {'fernet_key':Fernet.generate_key()}, 5),
    ('searchindex.js', TarZstdFernetFile, {Fernet.generate_key()}, fernetfile.open, {'fernet_key':Fernet.generate_key()}, 5),
    ('searchindex.js', TarZstdFernetFile, {Fernet.generate_key()}, naclz_open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('searchindex.js', TarZstdFernetFile, {Fernet.generate_key()}, naclfile.open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('searchindex.js', TarZstdFernetFile, {Fernet.generate_key()}, None, None, 20),
    ('searchindex.js', TarZstdFernetFile, {Fernet.generate_key()}, zstd_open, {'fernet_key':Fernet.generate_key()}, 20),
    ('searchindex.js', TarZstdFernetFile, {Fernet.generate_key()}, fernetfile.open, {'fernet_key':Fernet.generate_key()}, 20),
    ('searchindex.js', TarZstdFernetFile, {Fernet.generate_key()}, naclz_open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 20),
    ('searchindex.js', TarZstdFernetFile, {Fernet.generate_key()}, naclfile.open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 20),
    ('library.pdf', TarZstdFernetFile, {Fernet.generate_key()}, None, None, 5),
    ('library.pdf', TarZstdFernetFile, {Fernet.generate_key()}, zstd_open, {'fernet_key':Fernet.generate_key()}, 5),
    ('library.pdf', TarZstdFernetFile, {Fernet.generate_key()}, fernetfile.open, {'fernet_key':Fernet.generate_key()}, 5),
    ('library.pdf', TarZstdFernetFile, {Fernet.generate_key()}, naclz_open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('library.pdf', TarZstdFernetFile, {Fernet.generate_key()}, naclfile.open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 5),
    ('library.pdf', TarZstdFernetFile, {Fernet.generate_key()}, None, None, 20),
    ('library.pdf', TarZstdFernetFile, {Fernet.generate_key()}, zstd_open, {'fernet_key':Fernet.generate_key()}, 20),
    ('library.pdf', TarZstdFernetFile, {Fernet.generate_key()}, fernetfile.open, {'fernet_key':Fernet.generate_key()}, 20),
    ('library.pdf', TarZstdFernetFile, {Fernet.generate_key()}, naclfile.open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 20),
    ('library.pdf', TarZstdFernetFile, {Fernet.generate_key()}, naclz_open, {'secret_key':utils.random(SecretBox.KEY_SIZE)}, 20),
])
def test_benchmark_fstore(random_path, dt, cls, key, secure_open, secure_params, nb_doc):
    dataf = os.path.join(random_path, 'test.frnt')
    time_start = time.time()
    times = []
    file_size = 0
    with CofferStore(dataf, mode='w',
            container_class=cls, container_params=key,
            secure_open=secure_open, secure_params=secure_params) as ff:
        for i in range(nb_doc):
            if dt in ['download.html', 'genindex-all.html', 'searchindex.js']:
                df = os.path.join('python-3.13-docs-html', dt)
                ff.add(df, dt + '%s'%i)
                file_size += os.path.getsize(df)
            elif dt in [ 'library.pdf']:
                df = os.path.join('docs-pdf', dt)
                ff.add(df, dt + '%s'%i)
                file_size += os.path.getsize(df)
            times.append(time.time())
    time_write = time.time()
    with CofferStore(dataf, "rb",
            container_class=cls, container_params=key,
            secure_open=secure_open, secure_params=secure_params) as ff:
        ff.extractall('extract_tar')
    time_read = time.time()
    # ~ assert data == datar
    comp_size = os.path.getsize(dataf)
    for i in range(nb_doc):
        if dt in ['download.html', 'genindex-all.html', 'searchindex.js']:
            with open(os.path.join('python-3.13-docs-html', dt),'rb') as ff:
                data = ff.read()
            with open(os.path.join('extract_tar', dt + '%s'%i),'rb') as ff:
                datar = ff.read()
            assert data == datar
        elif dt in [ 'library.pdf']:
            with open(os.path.join('docs-pdf', dt),'rb') as ff:
                data = ff.read()
            with open(os.path.join('extract_tar', dt + '%s'%i),'rb') as ff:
                datar = ff.read()
            assert data == datar
    if secure_open == zstd_open:
        sopen = 'frnz'
    elif secure_open == fernetfile.open:
        sopen = 'frnt'
    elif secure_open == naclz_open:
        sopen = 'nacz'
    elif secure_open == naclfile.open:
        sopen = 'nacl'
    else:
        sopen = 'None'
    with open('BENCHMARK.md','at') as ff:
        ff.write("|%-18s | %6.0f | %-6s | %9.0f |  %9.0f | %7.2f | %5.2f | %5.2f | %5.2f | %5.2f | %5.2f | %5.2f |\n" %
        (dt, nb_doc, sopen, file_size / 1024, comp_size / 1024, comp_size / file_size * 100,
        time_write - time_start, time_read - time_write, times[-1] - times[-2], times[-2] - times[-3], times[-3] - times[-4], times[-4] - times[-5]))
