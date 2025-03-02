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
import secrets

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
import pycoffer.plugins.fido
from pycoffer.config import Config
from naclfile.zstd import NaclFile as ZstdNaclFile, open as naclz_open
from naclfile.tar import TarFile as TarZstdNaclFile

import pytest
from click.testing import CliRunner

KEY = b'qELXlwOZCyYlo9wU1hTYi8k51BRjyqc3phMamdhHVDOS0hVAaRgjgeM863mZlCtvAGJh5+jBgkhzTDzvhsNn1Jj/v1vy8itABp1IbJi2o+tiD9e9rVLwfOVxUmQ0zAW2'
# ~ KEY = b'SOEAFaPFfZ102Uf37/Qo9rQMlRXpqgO8aT4pri+Z3pHBqz2BABIb4Yw8CbqS0PRjOf6qXVwhxJnbHavk0G3GDgxPLmGFlu7yNXzjoC5CehXdlCUOpvBL2Hwfz7AmvAsW'

KEYPRV = b'HE7dpYn3/s+1JbEnm/EgMMBNGI2Y4chha523Gi7zPes='
KEYS = [
b'aEaYz4Gboh25FScc4osEPiAw0lw9J6yNKddKdVWQ8ifvsJ6mex58KSplhJELOiHK/SfmfHlllzbLdBd1WpqXhMd1FkdGE+gRivKaOUElLuET2AK2egJW+AiRDb4/eAG7',
b'cxs3A5gRquOOkSB0Nv0TfYt/7s8rf7ht+jiLgL7CgOddod75BNhPNTn2uPbUP6N7y2e7Fz/Yu63+7YrDx+4APtnMXu8Y50Qr02ANim5guwWpGfoaDhI83RgsMGuKbUZY',
]

try:
    import fido2.client
    import pycoffer.plugins.fido
    FIDO = len(list(pycoffer.plugins.fido.Fido.get_devices()))
except (ImportError,):
    FIDO = 0

@pytest.mark.skipif(FIDO < 1, reason="Need FIDO device")
@pytest.mark.skip(reason="Manual test to register keys.")
def notest_plugin_fido_keys(random_path, random_name):
    import fido2.client
    keyprv = secrets.token_bytes(32)
    print("keyprv", base64.b64encode(keyprv))
    for key in pycoffer.plugins.fido.Fido.get_devices():
        ident_prv, ident = pycoffer.plugins.fido.Fido.register(key, ident=keyprv)
        assert len(ident) == 96
        print("ident %s"%dev, base64.b64encode(ident))
    assert False

@pytest.mark.skipif(FIDO < 1, reason="Need FIDO device")
def test_plugin_fido_lib(random_path, random_name):
    import fido2.client
    for key in pycoffer.plugins.fido.Fido.get_devices():
        salt = secrets.token_bytes(32)
        for KEY in KEYS:
            ident = base64.b64decode(KEY)
            try:
                hkey = pycoffer.plugins.fido.Fido.derive(key, ident, salt, salt)
            except (fido2.client.ClientError, IndexError):
                continue
        assert len(hkey[0]) == 43
        assert len(hkey[1]) == 43

@pytest.mark.skipif(FIDO < 1, reason="Need FIDO device")
def test_plugin_fido_hmac(random_path, random_name):
    import aesfile
    import fido2.client
    salts = []
    aessalt = secrets.token_bytes(16)
    salt = secrets.token_bytes(32)
    key = list(pycoffer.plugins.fido.Fido.get_devices())[0]
    for KEY in KEYS:
        ident = base64.b64decode(KEY)
        try:
            hkey = pycoffer.plugins.fido.Fido.derive(key, ident, salt)
            _, res = aesfile.AesCryptor.derive(hkey[0], salt=aessalt)
            salts.append(res)
            hkey = pycoffer.plugins.fido.Fido.derive(key, ident, salt)
            _, res = aesfile.AesCryptor.derive(hkey[0], salt=aessalt)
            salts.append(res)
            break
        except (fido2.client.ClientError, IndexError):
            continue
    assert len(salts) == 2
    text = secrets.token_bytes(3268)
    cryp0 = aesfile.AesCryptor(aes_key=salts[0])
    cryp1 = aesfile.AesCryptor(aes_key=salts[1])
    crypted = cryp0._encrypt(text)
    uncrypted = cryp0._decrypt(crypted)
    assert uncrypted == text
    uncrypted = cryp1._decrypt(crypted)
    assert uncrypted == text

@pytest.mark.skipif(FIDO < 2, reason="Need 2 FIDO devices")
def test_plugin_fido_aes_crypt(random_path, random_name):
    import aesfile
    import fido2.client
    salts = []
    aessalt = secrets.token_bytes(16)
    salt = secrets.token_bytes(32)
    for key in pycoffer.plugins.fido.Fido.get_devices():
        for KEY in KEYS:
            ident = base64.b64decode(KEY)
            if KEY == KEYS[0]:
                try:
                    hkey = pycoffer.plugins.fido.Fido.derive(key, ident, salt)
                    _, res = aesfile.AesCryptor.derive(hkey[0], salt=aessalt)
                    salts.append(res)
                except (fido2.client.ClientError, IndexError):
                    continue
            try:
                hkey = pycoffer.plugins.fido.Fido.derive(key, ident, salt)
                _, res = aesfile.AesCryptor.derive(hkey[0], salt=aessalt)
                salts.append(res)
                break
            except (fido2.client.ClientError, IndexError):
                continue
    assert len(salts) == 3
    text = secrets.token_bytes(3268)
    cryp0 = aesfile.AesCryptor(aes_key=salts[0])
    cryp1 = aesfile.AesCryptor(aes_key=salts[1])
    cryp2 = aesfile.AesCryptor(aes_key=salts[2])
    crypted = cryp0._encrypt(text)
    uncrypted = cryp0._decrypt(crypted)
    assert uncrypted == text
    uncrypted = cryp1._decrypt(crypted)
    assert uncrypted == text
    uncrypted = cryp2._decrypt(crypted)
    assert uncrypted == text

@pytest.mark.skipif(FIDO < 2, reason="Need 2 FIDO devices")
def test_plugin_fido_nacl_crypt(random_path, random_name):
    print(list(pycoffer.plugins.fido.Fido.get_devices()))
    print(FIDO)
    import naclfile
    from nacl import utils
    from nacl.secret import SecretBox
    import fido2.client
    salts = []
    naclsalt = secrets.token_bytes(16)
    salt = secrets.token_bytes(32)
    for key in pycoffer.plugins.fido.Fido.get_devices():
        for KEY in KEYS:
            ident = base64.b64decode(KEY)
            if KEY == KEYS[0]:
                try:
                    hkey = pycoffer.plugins.fido.Fido.derive(key, ident, salt)
                    _, res = naclfile.NaclCryptor.derive(hkey[0], salt=naclsalt)
                    salts.append(res)
                except (fido2.client.ClientError, IndexError):
                    continue
            try:
                hkey = pycoffer.plugins.fido.Fido.derive(key, ident, salt)
                _, res = naclfile.NaclCryptor.derive(hkey[0], salt=naclsalt)
                salts.append(res)
                break
            except (fido2.client.ClientError, IndexError):
                continue
    assert len(salts) == 3
    assert len(salts[0]) == SecretBox.KEY_SIZE
    assert len(salts[1]) == SecretBox.KEY_SIZE
    assert len(salts[2]) == SecretBox.KEY_SIZE
    text = secrets.token_bytes(3268)
    cryp0 = naclfile.NaclCryptor(secret_key=salts[0])
    cryp1 = naclfile.NaclCryptor(secret_key=salts[1])
    cryp2 = naclfile.NaclCryptor(secret_key=salts[2])
    # ~ cryp0 = naclfile.NaclCryptor(secret_key=salts[0].encode())
    # ~ cryp1 = naclfile.NaclCryptor(secret_key=salts[1].encode())
    crypted = cryp0._encrypt(text)
    uncrypted = cryp0._decrypt(crypted)
    assert uncrypted == text
    uncrypted = cryp1._decrypt(crypted)
    assert uncrypted == text
    uncrypted = cryp2._decrypt(crypted)
    assert uncrypted == text

    # ~ assert False
