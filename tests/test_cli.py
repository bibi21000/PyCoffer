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

# ~ from cryptography.fernet import Fernet
from nacl import utils
from nacl.secret import SecretBox
from Crypto.Random import get_random_bytes

from pycoffer import config
from pycoffer import main
from pycoffer import main_cli
from pycoffer.coffers.bank import CofferBank
from pycoffer.plugins import Plugin
from pycoffer.config import Config

import pytest

def test_config(random_path, random_name):
    fname = os.path.join(random_path, 'config.ini')
    with open(fname, 'wb') as f:
        f.write(b'')
    confcoff = config.Config(fname, chkmode=False)

    assert confcoff.get_defaults() == {'ext': '.pcof'}

    with pytest.raises(PermissionError):
        assert confcoff.check_perms() is False

    assert confcoff.check_perms(exc=False) is False

    os.chmod(fname, 0o600)
    assert confcoff.check_perms()

    fname = 'tests/pycofferrc'
    confcoff = config.Config(fname, chkmode=False)
    assert confcoff.get_defaults() != {}
    coffer = confcoff.coffer('confidential')
    assert coffer is not None
    assert coffer['class'] == CofferBank
    print(base64.b64encode(utils.random(SecretBox.KEY_SIZE)))
    # ~ print(base64.b64encode(Fernet.generate_key()))
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
        assert ff.readable

    with coffer['class'](coffer['location'], "rb", coffer_key=coffer['coffer_key'], secure_key=coffer['secure_key'], backup=coffer['backup']) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

def test_config_generate(random_path, random_name):

    config = Config.generate(
        'test%s'%random_name,
        type='market')

    assert Config.Defaults() == {'ext': '.pcof'}

    assert Config.generate('test', type='bank', location='rrrrd') is not None

    assert Config.generate('test', type='bank', backup='.back') is not None

    assert Config.generate('test', type='market') is not None

    assert Config.generate('test', type='market', filename='tests/pycofferrc') is not None

    conf = Config('tests/pycofferrc')
    assert conf.generate('test', type='market') is not None

    assert conf.coffer('confidential') is not None

    with pytest.raises(KeyError):
        assert conf.coffer(None) is not None

    with pytest.raises(IndexError):
        assert conf.generate('test', type='baaad') is not None

def test_main_ls_empty(coffer_conf):
    runner = CliRunner()
    result = runner.invoke(main_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    assert result.exit_code == 1
    assert result.output == ''

def test_main_ls(coffer_conf):
    confcoff = Config(coffer_conf, chkmode=False)
    cofferfactory = confcoff.coffer('test')
    data = randbytes(178)
    with cofferfactory['class'](cofferfactory['location'], mode='wb') as ff:
        ff.write(data, 'file1.data')

    runner = CliRunner()
    result = runner.invoke(main_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    assert result.exit_code == 0
    assert 'file1.data' in result.output

def test_main_check_system(coffer_conf):

    runner = CliRunner()
    result = runner.invoke(main_cli.check, [])
    # ~ assert 'Cryptors' in result.output
    assert result.exit_code == 0

    result = runner.invoke(main_cli.check, ['system'])
    assert result.exit_code == 0
    assert 'Cryptors' in result.output

def test_main_generate_bank(random_path, coffer_conf):
    runner = CliRunner()
    result = runner.invoke(main_cli.generate, ['--coffer', 'test', '--type', 'bank', '--location', random_path])
    assert result.exit_code == 0
    assert 'type: bank' in result.output
    assert 'name: test' in result.output
    assert 'coffer_key' in result.output
    assert 'secure_key' in result.output

    with open(coffer_conf, 'wt') as f:
        for li in result.output.split('\n'):
            f.write(li + '\n')
            print(li)

    confcoff = Config(coffer_conf, chkmode=False)
    cofferfactory = confcoff.coffer('test')
    data = randbytes(178)

    with cofferfactory['class'](cofferfactory['location'], mode='wb',
        coffer_key=cofferfactory['coffer_key'], secure_key=cofferfactory['secure_key'],
        backup=cofferfactory['backup'] ) as ff:
        ff.write(data, 'file1.data')

    result = runner.invoke(main_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    assert result.exit_code == 0
    assert 'file1.data' in result.output

def test_main_add_delete_ls_extract(random_path, coffer_conf):
    data = randbytes(589)
    dataf = os.path.join(random_path, 'file1.data')
    with open(dataf, 'ab') as f:
        f.write(data)

    runner = CliRunner()
    result = runner.invoke(main_cli.add, ['--conf', coffer_conf, '--coffer', 'test',
            '--source', dataf, '--target', 'file1.data'])
    assert result.exit_code == 0

    result = runner.invoke(main_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    assert result.exit_code == 0
    assert 'file1.data' in result.output

    result = runner.invoke(main_cli.add, ['--conf', coffer_conf, '--coffer', 'test',
            '--source', dataf, '--target', 'test2/file1.data'])
    assert result.exit_code == 0

    result = runner.invoke(main_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    assert result.exit_code == 0
    assert 'file1.data' in result.output
    assert 'test2/file1.data' in result.output

    edir = os.path.join(random_path,'extract1')

    result = runner.invoke(main_cli.extract, ['--conf', coffer_conf, '--coffer', 'test',
            '--path', edir])
    assert result.exit_code == 1

    result = runner.invoke(main_cli.extract, ['--conf', coffer_conf, '--coffer', 'test',
            '--file', 'test2/file1.data', '--path', edir])
    assert result.exit_code == 0
    with open(os.path.join(edir,'test2/file1.data'), 'rb') as f:
        assert data == f.read()

    edir = os.path.join(random_path,'extract2')
    result = runner.invoke(main_cli.extract, ['--conf', coffer_conf, '--coffer', 'test',
            '--all', '--path', edir])
    assert result.exit_code == 0
    with open(os.path.join(edir,'test2/file1.data'), 'rb') as f:
        assert data == f.read()
    with open(os.path.join(edir,'file1.data'), 'rb') as f:
        assert data == f.read()

    result = runner.invoke(main_cli.delete, ['--conf', coffer_conf, '--coffer', 'test',
            '--force', '--file', 'test2/file1.data'])
    assert result.exit_code == 0

    result = runner.invoke(main_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    assert result.exit_code == 0
    assert 'file1.data' in result.output
    assert 'test2/file1.data' not in result.output

def test_config_baad(random_path, random_name):
    with pytest.raises(ValueError):
        assert Config.generate() is not None

    with pytest.raises(ValueError):
        assert Config.generate('test') is not None

    with pytest.raises(IndexError):
        assert Config.generate('test', type='eeee') is not None

    assert Config.generate('test', type='bank', location='rrrrd') is not None

    assert Config.generate('test', type='bank', backup='.back') is not None

    assert Config.generate('test', type='market') is not None
    # ~ conf = Config('tests/pycofferrc')
    # ~ assert conf.coffer('confidential') is not None
    # ~ assert conf.check_perms() is not None

def test_main_static(coffer_conf):
    import pycoffer.main_static
