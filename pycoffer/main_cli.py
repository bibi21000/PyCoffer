# -*- encoding: utf-8 -*-
""" pyfernet main script.

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import click

from . import main_lib

@click.group()
@click.version_option()
def cli():
    pass


@cli.command(help='Generate configuration for a new coffer.')
@click.option('-f', "--coffer",
    help='The coffer name.',
    show_default=True, required=True)
@click.option("--type", help='Type of coffer to use.',
    default=main_lib.defaults['type'] if 'type' in main_lib.defaults else 'bank',
    show_default=True)
@click.option("--location", help='Location of the store.',
    default=main_lib.defaults['location'] if 'location' in main_lib.defaults else None,
    show_default=True)
@click.option("--backup", help='Backup extension for files. None to disable.',
    default=main_lib.defaults['backup'] if 'backup' in main_lib.defaults else None,
    show_default=True)
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
    with main_lib.open_coffer(conf, coffer, 'r') as ff:
        for member in ff.getmembers():
            print(member.name, member.filesize)

@cli.command(help='Add file/directory in coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option('-s', "--source", help='The file/directory to add to coffer.')
@click.option('-t', "--target", help='The target in coffer. if None, the basename is used.')
@click.option("--replace", is_flag=True, show_default=True, default=False, help="Replace file in coffer if already exists.")
def add(conf, coffer, source, target, replace):
    with main_lib.open_coffer(conf, coffer, 'a') as ff:
        ff.add(source, arcname=target, replace=replace)

@cli.command(help='Delete file in coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option('-f', "--file", help='The file to delete in coffer.')
@click.option("--force", is_flag=True, show_default=True, default=False, help="Delete file without confirmation.")
def delete(conf, coffer, file, force):
    if force is False:
        raise RuntimeError('Not Implemented')
    with main_lib.open_coffer(conf, coffer, 'a') as ff:
        ff.delete(file)

@cli.command(help='Extract files from coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option('-p', "--path", help='The path to extract files.')
@click.option('-i', "--file", help='The file to extract from coffer.')
@click.option("--all", is_flag=True, show_default=True, default=False, help="Extract all file.")
def extract(conf, coffer, path, file, all):
    if file is None and all is False:
        raise RuntimeError('Use one --file or --all options')
    if file is not None:
        with main_lib.open_coffer(conf, coffer, 'r') as ff:
            ff.extract(file, path=path)
    else:
        with main_lib.open_coffer(conf, coffer, 'r') as ff:
            ff.extractall(path=path)

@cli.group(help='Check tools.')
def check():
    pass

@check.command(help='Print system informations.')
def system():
    from .plugins import Plugin
    import platform
    cryptors = [c.__name__ for c in Plugin.collect(group='cofferfile.cryptor')]
    print('Cryptors : %s' % cryptors)
    coffers = [c.__name__ for c in Plugin.collect(group='cofferfile.coffer')]
    print('Coffers : %s' % coffers)
    plugins = [c.__name__ for c in Plugin.collect(group='cofferfile.plugin')]
    print('Plugins : %s' % plugins)
    print(f'Python : {platform.python_version()} ({platform.python_implementation()})')
    print(f'Architecture : {platform.system()} ({platform.release()}) / {platform.machine()}')
    print(f'System : {platform.version()}')
    try:
        with open('/etc/issue', 'r') as f:
            os = f.read().split('\n')[0]
        print(f'Os : {os}')
    except Exception:
        pass
    try:
        print(f'Specific : {platform.libc_ver()}')
    except Exception:
        pass
    try:
        import subprocess
        ret = subprocess.run(["ldd", 'pycoffer_static.bin'], capture_output=True, text=True)
        ret = [r.strip() for r in ret.stdout.split('\n') if r.strip() != '']
        print(f'Ldd : {ret}')
    except Exception:
        pass
