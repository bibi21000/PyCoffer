# -*- encoding: utf-8 -*-
"""Crypt plugin Click interface

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import click

from pycoffer import main_lib

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

@cli.command(help='Decrypt file with keys of coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option('-s', "--source", help='The source encrypted file to decrypt.')
@click.option('-t', "--target", help='The target clear file.')
def decrypt(conf, coffer, source, target):
    with main_lib.open_coffer(conf, coffer, 'r') as ff:
        with ff.plugin('crypt') as plg:
            plg.decrypt(source, target)
