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
import logging

from cryptography.fernet import Fernet
from nacl import utils
from nacl.secret import SecretBox

from pycoffer import config
from pycoffer import main
from pycoffer import main_cli
from pycoffer import CofferInfo, Coffer, open as store_open
from pycoffer.bank import CofferBank
from pycoffer.plugins import Plugin
import pycoffer.plugins.password_cli
import pycoffer.plugins.crypt_cli
import pycoffer.plugins.rsync_cli
from pycoffer.config import Config
from naclfile.zstd import NaclFile as ZstdNaclFile, open as naclz_open
from naclfile.tar import TarFile as TarZstdNaclFile

import pytest
from click.testing import CliRunner

def test_plugin(random_path, random_name):
    print(Plugin.collect())
    print(Plugin.collect_cli())
    # ~ assert False

def test_plugin_password(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG, logger="pycoffer")
    key = utils.random(SecretBox.KEY_SIZE)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='ab', container_class=TarZstdNaclFile, container_params={'secret_key':key}) as ff:
        with ff.plugin('password') as plg:
            dpass = plg.Info(name='test', username='username', url='testurl', password='azerty', note='testnote')
            plg.add(dpass)

    with Coffer(dataf, mode='ab', container_class=TarZstdNaclFile, container_params={'secret_key':key}) as ff:
        with ff.plugin('password') as plg:
            dpass = plg.Info(name='test', username='username', url='testurl', password='azerty', note='testnote')
            plg.import_chrome('tests/chrome-password.csv')


    with Coffer(dataf, "rb", container_class=TarZstdNaclFile, container_params={'secret_key':key}) as ff:
        with ff.plugin('password') as plg:
            assert plg.get((None,'test')).username == 'username'

    # ~ pwdcls = Plugin.collect(name='password')[0]
    # ~ assert pwdcls is not None
    # ~ pwdplg = pwdcls()
    # ~ pwdplg.getmembers()
    # ~ with pytest.raises(ValueError):
        # ~ pwdplg.add(None)
    # ~ dpass = pwdplg.Info(name='test', username='username', url='testurl', password='azerty', note='testnote')
    # ~ pwdplg.add(dpass)
    # ~ with pytest.raises(IndexError):
        # ~ pwdplg.add(dpass, replace=False)
    # ~ members = pwdplg.getmembers()
    # ~ assert len(members) > 0
    # ~ infpass = pwdplg.get((None,'test'))
    # ~ print(infpass)
    # ~ assert infpass.username == 'username'
    # ~ pwdplg.import_chrome('tests/chrome-password.csv')
    # ~ assert pwdplg.get(('chrome','toto.com')).username == 'user'

def test_plugin_password_coffer(random_path, random_name):
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
        assert ff.readable

    with coffer['class'](coffer['location'], "rb", coffer_key=coffer['coffer_key'], secure_key=coffer['secure_key'], backup=coffer['backup']) as ff:
        assert data == ff.read('file1%s.data'%random_name)
        assert data2 == ff.read('file2%s.data'%random_name)
        assert not ff.writable
        assert ff.readable

def test_password_ls_empty(coffer_conf):
    runner = CliRunner()
    result = runner.invoke(pycoffer.plugins.password_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    assert result.exit_code == 1
    # ~ assert result.output == ''

def test_password_add_ls(coffer_conf):
    confcoff = Config(coffer_conf, chkmode=False)
    cofferfactory = confcoff.coffer('test')

    runner = CliRunner()

    result = runner.invoke(pycoffer.plugins.password_cli.add, ['--conf', coffer_conf, '--coffer', 'test',
        '--username', 'testuser', '--name', 'testname', '--url', 'https://test.url', '--password', 'azerty'])
    assert result.exit_code == 0
    # ~ assert 'file1.data' in result.output

    result = runner.invoke(pycoffer.plugins.password_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    assert result.exit_code == 0
    assert 'https://test.url' in result.output

    result = runner.invoke(pycoffer.plugins.password_cli.delete, ['--conf', coffer_conf, '--coffer', 'test', '--name', 'testname'])
    assert result.exit_code == 0
    # ~ assert "" == result.output

    result = runner.invoke(pycoffer.plugins.password_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    assert result.exit_code == 0
    assert 'https://test.url' not in result.output

    result = runner.invoke(pycoffer.plugins.password_cli.import_chrome, ['--conf', coffer_conf, '--coffer', 'test', '--file', 'tests/chrome-password.csv'])
    assert result.exit_code == 0

    result = runner.invoke(pycoffer.plugins.password_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    assert result.exit_code == 0
    assert 'www.totoaucongo.com' in result.output

    result = runner.invoke(pycoffer.plugins.password_cli.show, ['--conf', coffer_conf, '--coffer', 'test', '--name', 'tata.com', '--owner', 'chrome'])
    assert result.exit_code == 0

#    result = runner.invoke(pycoffer.plugins.password_cli.clip, ['--conf', coffer_conf, '--coffer', 'test', '--name', 'tata.com', '--owner', 'chrome'])
#    assert result.exit_code == 0

def test_plugin_crypt(random_path, coffer_conf):
    data = randbytes(4523)
    dataf = os.path.join(random_path, 'file1.data')
    datac = os.path.join(random_path, 'file1.datae')
    datad = os.path.join(random_path, 'file1.datad')
    with open(dataf, 'ab') as f:
        f.write(data)
    runner = CliRunner()

    # Need an existing coffer file
    result = runner.invoke(main_cli.add, ['--conf', coffer_conf, '--coffer', 'test',
            '--source', dataf, '--target', 'file1.data'])
    assert result.exit_code == 0

    result = runner.invoke(pycoffer.plugins.crypt_cli.crypt, ['--conf', coffer_conf, '--coffer', 'test',
        '--source', dataf, '--target', datac])
    assert result.exit_code == 0
    # ~ assert result.output == 'ddd'
    assert os.path.isfile(datac)

    result = runner.invoke(pycoffer.plugins.crypt_cli.decrypt, ['--conf', coffer_conf, '--coffer', 'test',
        '--source', datac, '--target', datad])
    assert result.exit_code == 0
    # ~ assert result.output == 'ddd'
    assert os.path.isfile(datad)

    with open(datad, 'rb') as f:
        assert data == f.read()

def test_plugin_rsync(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG, logger="pycoffer")
    key = utils.random(SecretBox.KEY_SIZE)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    with Coffer(dataf, mode='ab', container_class=TarZstdNaclFile, container_params={'secret_key':key}) as ff:
        with ff.plugin('rsync') as plg:
            plg.rsync('src', 'target')

def test_plugin_rsync_cli(coffer_conf):
    confcoff = Config(coffer_conf, chkmode=False)
    cofferfactory = confcoff.coffer('test')

    runner = CliRunner()

    result = runner.invoke(pycoffer.plugins.rsync_cli.rsync, ['--conf', coffer_conf, '--coffer', 'test',
        '--source', 'source', '--target', 'target'])
    assert result.exit_code == 0
    # ~ assert 'file1.data' in result.output

