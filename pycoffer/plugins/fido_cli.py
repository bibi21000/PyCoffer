# -*- encoding: utf-8 -*-
"""FIDO plugin Click interface

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import click

from pycoffer import main_lib
from pycoffer import main_cli

# ~ @click.group(help='Manage passwords in coffer.')
# ~ @click.command(help='Manage passwords in coffer.')
# ~ def password():
    # ~ pass

@click.group()
def cli():
    pass

@cli.command(help='Crypt file with keys of coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option('-s', "--source", help='The source clear file to encrypt.')
@click.option('-t', "--target", help='The target encrypted file.')
def crypt(conf, coffer, source, target):
    with main_lib.open_coffer(conf, coffer, 'r') as ff:
        with ff.plugin('crypt') as plg:
            plg.encrypt(source, target)

@main_cli.check.command(help='Check fidos adaptaters.')
@click.option("--all", is_flag=True, show_default=True, default=False, help="List all devices. Otherwise list only compatible devices.")
@click.option("--details", is_flag=True, show_default=True, default=False, help="Show all informations.")
def fido(all, details):
    from .fido import Fido
    if all:
        kwargs = {"extension": None}
    else:
        kwargs = {}
    for device in Fido.get_devices(**kwargs):
        infos = Fido.get_infos(device)
        if details:
            import pprint
            pprint.pprint(infos)
        else:
            print(f"{'%s(%s)'%(infos['path'],infos['usb_id']):24} : {infos['product_name']:40} {' '.join(infos['info'].versions):50}")

# ~ {'device': "CtapHidDevice('/dev/hidraw3')", 'product_name': 'ExcelSecu FIDO2 Security Key', 'serial_number': 'None', 'usb_id': '1ea8:fc26', 'path': '/dev/hidraw3', 'capabilities': {'WINK': True, 'LOCK': False, 'CBOR': True, 'NMSG': False}, 'info': Info(versions=['U2F_V2', 'FIDO_2_0', 'FIDO_2_1_PRE'], extensions=['credProtect', 'hmac-secret'], aaguid=AAGUID(20f0be98-9af9-986a-4b42-8eca4acb28e4), options={'rk': True, 'up': True, 'uv': False, 'plat': False, 'uvToken': False, 'clientPin': True, 'credentialMgmtPreview': True, 'userVerificationMgmtPreview': False}, max_msg_size=2048, pin_uv_protocols=[1], max_creds_in_list=8, max_cred_id_length=96, transports=['usb'], algorithms=[{'alg': -7, 'type': 'public-key'}], max_large_blob=None, force_pin_change=False, min_pin_length=4, firmware_version=None, max_cred_blob_length=None, max_rpids_for_min_pin=0, preferred_platform_uv_attempts=None, uv_modality=None, certifications=None, remaining_disc_creds=None, vendor_prototype_config_commands=None)}
        # ~ ff.write("|%-18s |%-18s | %6.0f | %9.0f |  %9.0f | %7.2f | %6.2f | %6.2f | %5.2f | %5.2f | %5.2f | %5.2f |\n" %
