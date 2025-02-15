# -*- encoding: utf-8 -*-
"""Password plugin Click interface

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import click

from .. import main_lib

@click.group(help='Manage passwords in coffer')
def password():
    pass

@main_lib.opt_configuration
@main_lib.opt_store
def ls(conf, store):
    with main_lib.open_coffer(conf, store, 'r') as ff:
        for member in ff.getmembers():
            print(member.name, member.filesize)

@password.command()
@click.argument("a", type=click.FLOAT)
@click.argument("b", type=click.FLOAT)
def password_copy(a, b):
    click.echo(a - b)

