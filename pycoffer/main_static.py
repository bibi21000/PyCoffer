# -*- encoding: utf-8 -*-
""" pyfernet main script.

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import click

# AesFile
import aesfile
import aesfile.tar
import aesfile.zstd

# FernetFile
# import fernetfile
# import fernetfile.tar
# import fernetfile.zstd

# NaclFile
import naclfile
import naclfile.tar
import naclfile.zstd

# PyCoffer
from pycoffer import main_cli

from pycoffer import bank
from pycoffer import store
from pycoffer import market
import pycoffer.null

from pycoffer.plugins import Plugin
from pycoffer.plugins import password
from pycoffer.plugins import password_cli
from pycoffer.plugins import crypt
from pycoffer.plugins import crypt_cli

plgs = [main_cli.cli] + [ plg.cli() for plg in Plugin.collect_cli()]
cli = click.CommandCollection(sources=plgs)
