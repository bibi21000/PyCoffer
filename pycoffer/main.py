# -*- encoding: utf-8 -*-
""" pyfernet main script.

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import click

@click.group()
def cli():
    pass

@cli.command()
@click.argument("-c", type=click.File("rb"), default='~/.pyfernetrc')
@click.argument("input", type=click.File("rb"), nargs=-1)
@click.argument("output", type=click.File("wb"))
def crypt(input, output):
    pass

    from fernetfile.zstd import FernetFile as ZstdFernetFile
    from fernetfile.zstd import CHUNK_SIZE, READ, WRITE, APPEND, EXCLUSIVE

@cli.command()
@click.argument("-c", type=click.File("rb"), default='~/.pyfernetrc')
def keygen(input, output):
    pass

    from fernetfile.zstd import FernetFile as ZstdFernetFile
    from fernetfile.zstd import CHUNK_SIZE, READ, WRITE, APPEND, EXCLUSIVE

@cli.command()
@click.argument("-c", type=click.File("rb"), default='~/.pyfernetrc')
def check(input, output):
    pass

    from fernetfile.zstd import FernetFile as ZstdFernetFile
    from fernetfile.zstd import CHUNK_SIZE, READ, WRITE, APPEND, EXCLUSIVE

@cli.group()
@click.argument("-c", type=click.File("rb"), default='~/.pyfernetrc')
@click.argument("--store", type=click.File("wb"), default='~/.pyfernet.store')
def store():
    pass

@store.command()
def list(input, output):
    pass

    from fernetfile.zstd import FernetFile as ZstdFernetFile
    from fernetfile.zstd import CHUNK_SIZE, READ, WRITE, APPEND, EXCLUSIVE

@store.command()
def add(input, output):
    pass

    from fernetfile.zstd import FernetFile as ZstdFernetFile
    from fernetfile.zstd import CHUNK_SIZE, READ, WRITE, APPEND, EXCLUSIVE

@store.command()
def extractall(input, output):
    pass

    from fernetfile.zstd import FernetFile as ZstdFernetFile
    from fernetfile.zstd import CHUNK_SIZE, READ, WRITE, APPEND, EXCLUSIVE

@store.command()
def extract(input, output):
    pass

    from fernetfile.zstd import FernetFile as ZstdFernetFile
    from fernetfile.zstd import CHUNK_SIZE, READ, WRITE, APPEND, EXCLUSIVE

@store.command()
def delete(input, output):
    pass

    from fernetfile.zstd import FernetFile as ZstdFernetFile
    from fernetfile.zstd import CHUNK_SIZE, READ, WRITE, APPEND, EXCLUSIVE

