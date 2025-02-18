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

@cli.command(help='Rsync directory with keys of coffer (to do).')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option('-s', "--source", help='The source directory.')
@click.option('-t', "--target", help='The target directory in coffer.')
def rsync(conf, coffer, source, target):
    with main_lib.open_coffer(conf, coffer, 'a') as ff:
        with ff.plugin('rsync') as plg:
            plg.rsync(source, target)
