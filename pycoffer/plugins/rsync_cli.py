# -*- encoding: utf-8 -*-
"""Crypt plugin Click interface

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import click

from pycoffer import main_lib

@click.group()
def cli():
    pass

@cli.command(help='Rsync directory with keys of coffer using mtime (to do).')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option('-s', "--source", help='The source directory.')
@click.option('-t', "--target", help='The target directory in coffer.')
@click.option("--dry", is_flag=True, show_default=True, default=False, help="Don't do anything, only show files that will be updated.")
def rsync(conf, coffer, source, target, dry):
    with main_lib.open_coffer(conf, coffer, 'a') as ff:
        with ff.plugin('rsync') as plg:
            ret = plg.rsync(source, target, dry)
            if dry is True:
                print(ret)
