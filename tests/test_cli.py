# -*- encoding: utf-8 -*-
"""Test module

"""
import os
import io
from random import randbytes
import tarfile
import lzma
import bz2
import zipfile
import struct
import shutil
import base64

from click.testing import CliRunner

from cryptography.fernet import Fernet
from nacl import utils
from nacl.secret import SecretBox

from pycoffer import config
from pycoffer import main
from pycoffer.bank import CofferBank
from pycoffer.plugins import Plugin
from pycoffer.config import Config

import pytest

def test_config(random_path, random_name):
    fname = os.path.join(random_path, 'config.ini')
    with open(fname, 'wb') as f:
        f.write(b'')
    confcoff = config.Config(fname, chkmode=False)

    with pytest.raises(PermissionError):
        assert confcoff.check_perms() is False

    assert confcoff.check_perms(exc=False) is False

    os.chmod(fname, 0o600)
    assert confcoff.check_perms()

    fname = 'tests/pycofferrc'
    confcoff = config.Config(fname, chkmode=False)
    coffer = confcoff.coffer('confidential')
    assert coffer is not None
    assert coffer['class'] == CofferBank
    print(base64.b64encode(utils.random(SecretBox.KEY_SIZE)))
    print(base64.b64encode(Fernet.generate_key()))
    # ~ assert False

    data = randbytes(2487)
    data2 = randbytes(1536)
    data2a = randbytes(7415)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with coffer['class'](coffer['location'], mode='wb', coffer_key=coffer['coffer_key'], secure_key=coffer['secure_key'], backup=coffer['backup']) as ff:
        assert repr(ff).startswith('<CofferBank')
        ff.write(data, 'file1%s.data'%random_name)
        ff.write(data2, 'file2%s.data'%random_name)
        mtime = ff.mtime
        assert ff.writable
        assert not ff.readable

    with coffer['class'](coffer['location'], "rb", coffer_key=coffer['coffer_key'], secure_key=coffer['secure_key'], backup=coffer['backup']) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

def test_config(random_path, random_name):

    config = Config.generate(
        store='test%s'%random_name,
        type='market')

    assert Config.generate(store='test', type='bank', location='rrrrd') is not None

    assert Config.generate(store='test', type='bank', backup='.back') is not None

    assert Config.generate(store='test', type='market') is not None
    conf = Config('tests/pycofferrc')
    assert conf.coffer('confidential') is not None

def test_hello_world():
  runner = CliRunner()
  result = runner.invoke(main.ls, ['--conf', 'tests/pycofferrc', '--store', 'confidential'])
  assert result.exit_code == 0
  # ~ assert result.output == 'Hello Peter!\n'

def test_config(random_path, random_name):
    with pytest.raises(ValueError):
        assert Config.generate() is not None

    with pytest.raises(ValueError):
        assert Config.generate(store='test') is not None

    with pytest.raises(IndexError):
        assert Config.generate(store='test', type='eeee') is not None

    assert Config.generate(store='test', type='bank', location='rrrrd') is not None

    assert Config.generate(store='test', type='bank', backup='.back') is not None

    assert Config.generate(store='test', type='market') is not None
    conf = Config('tests/pycofferrc')
    assert conf.coffer('confidential') is not None
    assert conf.check_perms() is not None
