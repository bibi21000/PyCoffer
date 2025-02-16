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
@click.version_option()
def cli():
    pass


@cli.command(help='Generate configuration for a new coffer.')
@main_lib.opt_coffer
@click.option("--type", help='Type of coffer to use.', default='bank')
@click.option("--location", help='Location of the store.')
@click.option("--backup", help='Backup extension for files. None to disable.')
def generate(coffer, type, location, backup):
    import os
    from .config import Config
    if location is None:
        location = os.getcwd()
    for line in Config.generate(coffer, type=type, location=location, backup=backup):
        print(line)

@cli.command(help='List files in coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
def ls(conf, coffer):
    with open_coffer(conf, coffer, 'r') as ff:
        for member in ff.getmembers():
            print(member.name, member.filesize)

@cli.command(help='Add file/directory in coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option('-s', "--source", help='Then file to add to coffer.')
@click.option('-t', "--target", help='The target in coffer. if None, the basename is used.')
@click.option("--replace", is_flag=True, show_default=True, default=False, help="Replace file in coffer if already exists.")
def add(conf, coffer, source, target, replace):
    with open_coffer(conf, coffer, 'a') as ff:
        ff.add(source, arcname=target, replace=replace)

@cli.command(help='Delete file in coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option('-f', "--file", help='The file to delete in coffer.')
@click.option("--force", is_flag=True, show_default=True, default=False, help="Delete file without confirmation.")
def delete(conf, coffer, file, force):
    if force is False:
        raise RuntimeError('Not Implemented')
    with open_coffer(conf, coffer, 'a') as ff:
        ff.delete(file)

@cli.command(help='Extract files from coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option('-p', "--path", help='The path to extract files.')
@click.option('-f', "--file", help='The file to extract from coffer.')
@click.option("--all", is_flag=True, show_default=True, default=False, help="Extract all file.")
def extract(conf, coffer, path, file, all):
    if file is None and all is False:
        raise RuntimeError('Use one --file or --all options')
    if file is not None:
        with open_coffer(conf, coffer, 'r') as ff:
            ff.extract(file, path=path)
    else:
        with open_coffer(conf, coffer, 'r') as ff:
            ff.extractall(path=path)

for plugin in Plugin.collect_cli():
    print(plugin.desc)
    cli.add_command(plugin.cli())
