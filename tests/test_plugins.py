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

from Crypto.Random import get_random_bytes
from nacl import utils
from nacl.secret import SecretBox

from pycoffer import config
from pycoffer import main
from pycoffer import main_cli
from pycoffer import CofferInfo, Coffer, open as store_open
from pycoffer.coffers.bank import CofferBank
from pycoffer.plugins import Plugin, PluginInfo
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
    assert repr(PluginInfo()).startswith('<PluginInfo')
    assert repr(Plugin.Info()).startswith('<PluginInfo')

    key = utils.random(SecretBox.KEY_SIZE)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)
    with pytest.raises(IndexError):
        with Coffer(dataf, mode='ab', container_class=TarZstdNaclFile, container_params={'secret_key':key}) as ff:
            with ff.plugin('toto') as plg:
                pass
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
    print(base64.b64encode(get_random_bytes(16)))
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

def test_plugin_rsync_lib(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG, logger="pycoffer")
    key = utils.random(SecretBox.KEY_SIZE)
    dataf = os.path.join(random_path, 'test%s.stzf'%random_name)

    data = randbytes(4523)
    data2 = randbytes(4523)
    os.makedirs(os.path.join(random_path, 'rsync_%s'%random_name))
    os.makedirs(os.path.join(random_path, 'rsync_%s'%random_name, 'test1'))
    os.makedirs(os.path.join(random_path, 'rsync_%s'%random_name, 'test1', 'test11'))
    os.makedirs(os.path.join(random_path, 'rsync_%s'%random_name, 'test2'))
    dataf1 = os.path.join(random_path, 'rsync_%s'%random_name, 'file1.data')
    dataf2 = os.path.join(random_path, 'rsync_%s'%random_name, 'test1', 'file1.data')
    dataf3 = os.path.join(random_path, 'rsync_%s'%random_name, 'test1', 'test11', 'file1.data')
    dataf4 = os.path.join(random_path, 'rsync_%s'%random_name, 'test2', 'file1.data')
    with open(dataf1, 'wb') as f:
        f.write(data)
    with open(dataf2, 'wb') as f:
        f.write(data)
    with open(dataf3, 'wb') as f:
        f.write(data)
    with open(dataf4, 'wb') as f:
        f.write(data)

    with Coffer(dataf, mode='ab', container_class=TarZstdNaclFile, container_params={'secret_key':key}) as ff:
        with ff.plugin('rsync') as plg:
            ret = plg.rsync(os.path.join(random_path, 'rsync_%s'%random_name), 'target')
            print(ret)
        membs = ff.getmembers()
        print(membs)

    tarpath = os.path.join(random_path, "extract_rsync_%s"%random_name)
    with Coffer(dataf, mode='rb', container_class=TarZstdNaclFile, container_params={'secret_key':key}) as ff:
        ff.extractall(path=tarpath)

    with open(os.path.join(tarpath, 'target', 'file1.data'), 'rb') as f:
        assert data == f.read()
    with open(os.path.join(tarpath, 'target', 'test1', 'file1.data'), 'rb') as f:
        assert data == f.read()
    with open(os.path.join(tarpath, 'target', 'test1', 'test11', 'file1.data'), 'rb') as f:
        assert data == f.read()
    with open(os.path.join(tarpath, 'target', 'test2', 'file1.data'), 'rb') as f:
        assert data == f.read()

    with open(dataf3, 'wb') as f:
        f.write(data2)

    with Coffer(dataf, mode='ab', container_class=TarZstdNaclFile, container_params={'secret_key':key}) as ff:
        with ff.plugin('rsync') as plg:
            ret = plg.rsync(os.path.join(random_path, 'rsync_%s'%random_name), 'target', dry=True)
            print(ret)
            assert len(ret) == 5
            assert ret[3] == 'found target/test1/test11/file1.data'
        membs = ff.getmembers()
        print(membs)

    with Coffer(dataf, mode='ab', container_class=TarZstdNaclFile, container_params={'secret_key':key}) as ff:
        with ff.plugin('rsync') as plg:
            ret = plg.rsync(os.path.join(random_path, 'rsync_%s'%random_name), 'target')
            print(ret)
            assert len(ret) == 1
            assert ret[0] == 'update target/test1/test11/file1.data'
        membs = ff.getmembers()
        print(membs)

    tarpath = os.path.join(random_path, "extract_rsync2_%s"%random_name)
    with Coffer(dataf, mode='rb', container_class=TarZstdNaclFile, container_params={'secret_key':key}) as ff:
        ff.extractall(path=tarpath)

    with open(os.path.join(tarpath, 'target', 'file1.data'), 'rb') as f:
        assert data == f.read()
    with open(os.path.join(tarpath, 'target', 'test1', 'file1.data'), 'rb') as f:
        assert data == f.read()
    with open(os.path.join(tarpath, 'target', 'test1', 'test11', 'file1.data'), 'rb') as f:
        assert data2 == f.read()
    with open(os.path.join(tarpath, 'target', 'test2', 'file1.data'), 'rb') as f:
        assert data == f.read()

def test_plugin_rsync_cli(coffer_conf, random_path, random_name):
    confcoff = Config(coffer_conf, chkmode=False)
    cofferfactory = confcoff.coffer('test')

    data = randbytes(4523)
    data2 = randbytes(4523)
    os.makedirs(os.path.join(random_path, 'rsync_%s'%random_name))
    os.makedirs(os.path.join(random_path, 'rsync_%s'%random_name, 'test1'))
    os.makedirs(os.path.join(random_path, 'rsync_%s'%random_name, 'test1', 'test11'))
    os.makedirs(os.path.join(random_path, 'rsync_%s'%random_name, 'test2'))
    dataf1 = os.path.join(random_path, 'rsync_%s'%random_name, 'file1.data')
    dataf2 = os.path.join(random_path, 'rsync_%s'%random_name, 'test1', 'file1.data')
    dataf3 = os.path.join(random_path, 'rsync_%s'%random_name, 'test1', 'test11', 'file1.data')
    dataf4 = os.path.join(random_path, 'rsync_%s'%random_name, 'test2', 'file1.data')
    with open(dataf1, 'wb') as f:
        f.write(data)
    with open(dataf2, 'wb') as f:
        f.write(data)
    with open(dataf3, 'wb') as f:
        f.write(data)
    with open(dataf4, 'wb') as f:
        f.write(data)

    runner = CliRunner()

    result = runner.invoke(pycoffer.plugins.rsync_cli.rsync, ['--conf', coffer_conf, '--coffer', 'test',
        '--source', os.path.join(random_path, 'rsync_%s'%random_name), '--target', 'test3'])
    assert result.exit_code == 0
    # ~ assert 'file1.data' in result.output

