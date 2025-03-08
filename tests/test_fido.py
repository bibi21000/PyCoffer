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
import pycoffer.plugins.fido_cli
import pycoffer.plugins.fido
from pycoffer.config import Config
from naclfile.zstd import NaclFile as ZstdNaclFile, open as naclz_open
from naclfile.tar import TarFile as TarZstdNaclFile

import pytest
from click.testing import CliRunner

RP_ID = 'pycoffertest'
RP_NAME = 'Pycoffer keys'
USER_IDENT = 'testuserpycoffer'
USER_NAME = 'pycoffer'
CREDS = [
b'\xeak\x14\xcd\xd1/\xf7\xa9\xc5\x97t\xcc\xbfD\xb3U#\xb6\x8f\x12\xad\xd4C"\nd\xe0\xab\xfd\xfc\xcd\xa3d[\x8f\xec\xff\xb2\xb0\xa3\x14\x94WH\xc9|\xe8\xc2\xc7\xcb\xf9\xf9\xbbU\xc1\xf0\xa1\x15\xd8\xb9\xc3\xd9Ud5\xaer^(\xbdX\x12\xddP\xfe\x9b\xd3W\x0f:\xa2\xc5\xbf\xd1Li\x8c\xc4.\xa6\x83$\x1fC&E',
b'\xb3\x12"Fo1\xe9\xc2i\xf9\x0f\x88\xca\xb5\xb9\xd7o\x94\x9e\xcf\xbc\xbf\xc4\xb6d\x84\xe7\xd4\x95\x03\x8bO',
b'\xb6\xda!\xd2\rR\xa3\xa8o\xf7?F>\x88\xee({Ed\x05\xd7\xb2\x97\x89\xb20V4\x9e\x9a\xb3v\x86@\\oUb\xb8\x80\xdf\xb2P\x0b]j\xa2\xb2\xc8h!\x1b\x98\x1b\\\xaf J\x1e\x98\xd9O8\xba\x83\x97\x0f3\xf9\xf0x\xac\x1a l\xe8~\xea\n\x92\xfe\\\xfc\xc3\xa7O\x9f\xfe{\xacK\xdbV\xa1\\\x8a',
b"\xf1\xbd\xc6\x03\x89\x8b\x12\xf1e%\xe4\xf4\x9ejM\x1e\x86\x16\xe8\x95\xba\x1f\x97V\x8d[\x8d]\xa2d;k\xbfp5\xd7\xbf*Ykx\xb4z\xf63C\xe6'\xa1n\xaa\xf6\x80\xbdM_2\x06/#\xac\x94\x85\xc39\xeb\x8c\x13\xb1\xcc\xe9\x87W\x10M[RH_\xaa\xfe\x044\t\xa2\xa4\x9c\x19e\x88j@\xcc\xb5\xae\x96",
]

try:
    import fido2.client
    import pycoffer.plugins.fido
    FIDO = len(list(pycoffer.plugins.fido.Fido.get_devices()))
except (ImportError,):
    FIDO = 0

@pytest.mark.skipif(FIDO < 1, reason="Need FIDO device")
@pytest.mark.skip(reason="Manual test to register keys.")
def test_plugin_fido_register(random_path, random_name):
    import fido2.client
    # ~ keyprv = secrets.token_bytes(32)
    # ~ print("keyprv", base64.b64encode(keyprv))
    for key in pycoffer.plugins.fido.Fido.get_devices():
        private, cert = pycoffer.plugins.fido.Fido.register(key, user_ident=USER_IDENT, user_name=USER_NAME, rp_id=RP_ID, rp_name=RP_NAME)
        # ~ assert len(ident) == 96
        print("private %s"%key, private)
        print("cert %s"%key, cert)
    assert False

@pytest.mark.skipif(FIDO < 1, reason="Need FIDO device")
@pytest.mark.skip(reason="Manual test to register keys.")
def test_plugin_fido_register_and_check(random_path, random_name):
    import fido2.client
    # ~ keyprv = secrets.token_bytes(32)
    # ~ print("keyprv", base64.b64encode(keyprv))
    for key in pycoffer.plugins.fido.Fido.get_devices():
        private, cert = pycoffer.plugins.fido.Fido.register(key, user_ident=USER_IDENT, user_name=USER_NAME, rp_id=RP_ID, rp_name=RP_NAME)
        # ~ assert len(ident) == 96
        print("private %s"%key, private)
        print("cert %s"%key, cert)
        assert pycoffer.plugins.fido.Fido.check(key, cred_id=cert['credential_id'], rp_id=RP_ID)

    assert False

@pytest.mark.skipif(FIDO < 1, reason="Need FIDO device")
def test_plugin_fido_check(random_path, random_name):
    import fido2.client
    for key in pycoffer.plugins.fido.Fido.get_devices():
        print("key %s"%key)
        registered = False
        for cred in CREDS:
            print("cred %s"%cred)
            ret = pycoffer.plugins.fido.Fido.check(key, cred_id=cred, rp_id=RP_ID)
            print(ret)
            if ret is True:
                registered = True
                break
        assert registered is True

@pytest.mark.skipif(FIDO < 1, reason="Need FIDO device")
def test_plugin_fido_derive(random_path, random_name):
    import fido2.client
    for key in pycoffer.plugins.fido.Fido.get_devices():
        salt = secrets.token_bytes(32)
        hkey = pycoffer.plugins.fido.Fido.derive(key, CREDS, RP_ID, salt, salt)
        assert len(hkey[0]) == 43
        assert len(hkey[1]) == 43

FORMAT = "|%-40s|%-20s|%-20s|%-20s|%-45s|%-10s|%-30s|%-8s|%-8s|%-8s|%-8s|%-8s|%-8s|%-8s|%-8s|%-8s|%-8s|%-8s|%-8s|%-8s|%-30s|\n"
def format_line(f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16, f17, f18, f19, f20, f21):
    return FORMAT%(f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16, f17, f18, f19, f20, f21)

def fill_list(list, size):
    while len(list) < size:
        list.append('')
    return list

def row(list, new=False):
    ret = []
    if new :
        new = '*'
    else:
        new = ' '
    if len(list) > 0:
        ret.append("   %s - | %s\n"%(new, list[0]))
    else:
        ret.append("   %s - | \n"%new)
    for v in list[1:]:
        ret.append("       | %s\n"%v)
    return ret

@pytest.mark.skipif(FIDO < 1, reason="Need FIDO device")
def test_plugin_fido_info(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG)
    import fido2.client
    for key in pycoffer.plugins.fido.Fido.get_devices(extension=None):
        infos = pycoffer.plugins.fido.Fido.get_infos(key)
        filename = infos['product_name'].replace(' ', '_')
        capabilities = ['%s:%s'%(k,v) for k,v in infos['capabilities'].items()]
        certifications = ['%s:%s'%(k,v) for k,v in infos['info'].certifications.items()] if infos['info'].certifications is not None else []
        options = ['%s:%s'%(k,v) for k,v in infos['info'].options.items()]
        versions = infos['info'].versions
        extensions = infos['info'].extensions
        pin_uv_protocols = [ '%s'%i for i in infos['info'].pin_uv_protocols]
        transports = infos['info'].transports
        vendor_prototype_config_commands = infos['info'].vendor_prototype_config_commands if infos['info'].vendor_prototype_config_commands is not None else []
        algorithms = []
        if infos['info'].algorithms is not None:
            for a in infos['info'].algorithms:
                algorithms.append('(' + ' '.join(['%s:%s'%(k,v) for k,v in a.items()]) +')')
        max_size = max([len(capabilities),len(certifications),len(options),len(pin_uv_protocols),len(vendor_prototype_config_commands)])
        with open(os.path.join("docs/dev/adaptaters", filename),'wt') as ff:
            ff.writelines(row([infos['product_name'], "(%s)" % (infos['usb_id']), "Firmware : %s"%infos['info'].firmware_version], new=True))
            ff.writelines(row(capabilities))
            ff.writelines(row(versions))
            ff.writelines(row(extensions))
            ff.writelines(row(options))
            ff.writelines(row(transports))
            ff.writelines(row(algorithms))
            ff.writelines(row(certifications))
            ff.writelines(row(pin_uv_protocols))
            ff.writelines(row([infos['info'].max_msg_size]))
            ff.writelines(row([infos['info'].max_creds_in_list]))
            ff.writelines(row([infos['info'].max_cred_id_length]))
            ff.writelines(row([infos['info'].max_large_blob]))
            ff.writelines(row([infos['info'].force_pin_change]))
            ff.writelines(row([infos['info'].min_pin_length]))
            ff.writelines(row([infos['info'].max_cred_blob_length]))
            ff.writelines(row([infos['info'].max_rpids_for_min_pin]))
            ff.writelines(row([infos['info'].preferred_platform_uv_attempts]))
            ff.writelines(row([infos['info'].uv_modality]))
            ff.writelines(row([infos['info'].remaining_disc_creds]))
            ff.writelines(row(vendor_prototype_config_commands))

@pytest.mark.skipif(FIDO < 1, reason="Need FIDO device")
# ~ @pytest.mark.skip(reason="Work in progress.")
def test_plugin_fido_list(caplog, random_path, random_name):
    caplog.set_level(logging.DEBUG)
    import fido2.client
    for key in pycoffer.plugins.fido.Fido.get_devices():
        pycoffer.plugins.fido.Fido.list_rps(key, '1405')
    assert False

@pytest.mark.skipif(FIDO < 1, reason="Need FIDO device")
def test_plugin_fido_hmac(random_path, random_name):
    import aesfile
    import fido2.client
    salts = []
    aessalt = secrets.token_bytes(16)
    salt = secrets.token_bytes(32)
    key = list(pycoffer.plugins.fido.Fido.get_devices())[0]
    for ident in CREDS:
        try:
            hkey = pycoffer.plugins.fido.Fido.derive_from_credential(key, ident, RP_ID, salt)
            _, res = aesfile.AesCryptor.derive(hkey[0], salt=aessalt)
            salts.append(res)
            hkey = pycoffer.plugins.fido.Fido.derive_from_credential(key, ident, RP_ID, salt)
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
        for ident in CREDS:
            try:
                hkey = pycoffer.plugins.fido.Fido.derive_from_credential(key, ident, RP_ID, salt)
                _, res = aesfile.AesCryptor.derive(hkey[0], salt=aessalt)
                salts.append(res)
            except (fido2.client.ClientError, IndexError):
                continue
    hkey = pycoffer.plugins.fido.Fido.derive(key, CREDS, RP_ID, salt)
    _, res = aesfile.AesCryptor.derive(hkey[0], salt=aessalt)
    salts.append(res)

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
        for ident in CREDS:
            try:
                hkey = pycoffer.plugins.fido.Fido.derive_from_credential(key, ident, RP_ID, salt)
                _, res = naclfile.NaclCryptor.derive(hkey[0], salt=naclsalt)
                salts.append(res)
            except (fido2.client.ClientError, IndexError):
                continue
    hkey = pycoffer.plugins.fido.Fido.derive(key, CREDS, RP_ID, salt)
    _, res = naclfile.NaclCryptor.derive(hkey[0], salt=naclsalt)
    salts.append(res)

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

def notest_plugin_fido_virtual(random_path, random_name, fido):
    device, ctap2 = fido
    rps = list(pycoffer.plugins.fido.Fido.list_rps(device, '1405'))
    # ~ import fido2.client
    # ~ from . import fido2_emulator
    # ~ device = fido2_emulator.VirtualCtapDevice()
    # ~ client = pycoffer.plugins.fido.Fido.get_client(device)
    # ~ print(device)
    # ~ rps = list(pycoffer.plugins.fido.Fido.list_rps(device, '1405'))
    # ~ ident_prv, ident = pycoffer.plugins.fido.Fido.register(device, ident='test'.encode())
    # ~ hkey = pycoffer.plugins.fido.Fido.derive(key, ident, salt)
    # ~ keyprv = secrets.token_bytes(32)
    # ~ print("keyprv", base64.b64encode(keyprv))
    # ~ keyprv = base64.b64decode(KEYPRV)
    # ~ for key in pycoffer.plugins.fido.Fido.get_devices():
        # ~ ident_prv, ident = pycoffer.plugins.fido.Fido.register(key, ident=keyprv)
        # ~ assert len(ident) == 96
        # ~ print("ident %s"%key, base64.b64encode(ident))
    # ~ assert False
    # ~ pycoffer.plugins.fido.Fido.get_devices()


def test_fido_cli_check(coffer_conf):
    confcoff = Config(coffer_conf, chkmode=False)

    runner = CliRunner()

    result = runner.invoke(pycoffer.plugins.fido_cli.fido, [])
    # ~ assert 'file1.data' in result.output
    assert result.exit_code == 0

    result = runner.invoke(pycoffer.plugins.fido_cli.fido, ['--all'])
    # ~ assert 'file1.data' in result.output
    assert result.exit_code == 0

    result = runner.invoke(pycoffer.plugins.fido_cli.fido, ['--all', '--details'])
    # ~ assert 'file1.data' in result.output
    assert result.exit_code == 0

    # ~ result = runner.invoke(pycoffer.plugins.password_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    # ~ assert result.exit_code == 0
    # ~ assert 'https://test.url' in result.output

    # ~ result = runner.invoke(pycoffer.plugins.password_cli.delete, ['--conf', coffer_conf, '--coffer', 'test', '--name', 'testname'])
    # ~ assert result.exit_code == 0
    # ~ assert "" == result.output

    # ~ result = runner.invoke(pycoffer.plugins.password_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    # ~ assert result.exit_code == 0
    # ~ assert 'https://test.url' not in result.output

    # ~ result = runner.invoke(pycoffer.plugins.password_cli.import_chrome, ['--conf', coffer_conf, '--coffer', 'test', '--file', 'tests/chrome-password.csv'])
    # ~ assert result.exit_code == 0

    # ~ result = runner.invoke(pycoffer.plugins.password_cli.ls, ['--conf', coffer_conf, '--coffer', 'test'])
    # ~ assert result.exit_code == 0
    # ~ assert 'www.totoaucongo.com' in result.output

    # ~ result = runner.invoke(pycoffer.plugins.password_cli.show, ['--conf', coffer_conf, '--coffer', 'test', '--name', 'tata.com', '--owner', 'chrome'])
    # ~ assert result.exit_code == 0

#    result = runner.invoke(pycoffer.plugins.password_cli.clip, ['--conf', coffer_conf, '--coffer', 'test', '--name', 'tata.com', '--owner', 'chrome'])
#    assert result.exit_code == 0
