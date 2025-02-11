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

from cryptography.fernet import Fernet

from cofferfile import cli

import pytest

def test_config(random_path):
    fname = os.path.join(random_path, 'config.ini')
    with open(fname, 'wb') as f:
        f.write(b'')
    config = cli.Config(fname, chkmode=False)

    with pytest.raises(PermissionError):
        assert config.check_perms() is False

    assert config.check_perms(exc=False) is False

    os.chmod(fname, 0o600)
    assert config.check_perms()
