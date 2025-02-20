# -*- encoding: utf-8 -*-
""" pycoffer main script.

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import click

from . import main_cli
from .plugins import Plugin


plgs = [main_cli.cli] + [ plg.cli() for plg in Plugin.collect_cli()]
cli = click.CommandCollection(sources=plgs)


