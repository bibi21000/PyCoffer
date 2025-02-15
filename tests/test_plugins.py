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
from pycoffer import CofferInfo, Coffer, open as store_open
from pycoffer.bank import CofferBank
from pycoffer.plugins import Plugin
from pycoffer.config import Config
from naclfile.zstd import NaclFile as ZstdNaclFile, open as naclz_open
from naclfile.tar import TarFile as TarZstdNaclFile

import pytest

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
