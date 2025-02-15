# -*- encoding: utf-8 -*-
""" pyfernet main script.

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import click

from . import main_lib
from .main_lib import open_coffer
from .plugins import Plugin

@click.group()
def cli():
    pass

@cli.command()
@click.argument("-c", type=click.File("rb"), default='~/.pycofferrc')
@click.argument("input", type=click.File("rb"), nargs=-1)
@click.argument("output", type=click.File("wb"))
def crypt(input, output):
    pass

@cli.command(help='Generate configuration for a new store')
@main_lib.opt_store
@click.option("--type", help='Type of coffer to use', default='bank')
@click.option("--location", help='Location of the store')
@click.option("--backup", help='Backup extension for files. None to disable')
def generate(store, type, location, backup):
    from .config import Config
    if location is not None and location.endswith('/'):
        location += store
    for line in Config.generate(store=store, type=type, location=location, backup=backup):
        print(line)

@cli.command()
@click.argument("-c", type=click.File("rb"), default='~/.pycofferrc')
def check(input, output):
    pass

@cli.command(help='List files in coffer')
@main_lib.opt_configuration
@main_lib.opt_store
def ls(conf, store):
    with open_coffer(conf, store, 'r') as ff:
        for member in ff.getmembers():
            print(member.name, member.filesize)

@cli.group()
@click.argument("-c", type=click.File("rb"), default='~/.pycofferrc')
@click.argument("--store", type=click.File("wb"), default='~/.pycofferrc')
def store():
    pass

@store.command()
def list(input, output):
    pass

@store.command()
def add(input, output):
    pass

@store.command()
def extractall(input, output):
    pass

@store.command()
def extract(input, output):
    pass

@store.command()
def delete(input, output):
    pass

for plugin in Plugin.collect_cli():
    cli.add_command(plugin.cli())
