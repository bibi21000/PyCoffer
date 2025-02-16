# -*- encoding: utf-8 -*-
""" pyfernet main script.

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import os
import click

from .config import Config

def open_coffer(conf, store, mode):
    from .config import Config
    confcoff = Config(conf, chkmode=True)
    coffer = confcoff.coffer(store)
    coffer_args = {}
    if 'coffer_key' in coffer:
        coffer_args['coffer_key'] = coffer['coffer_key']
    if 'secure_key' in coffer:
        coffer_args['secure_key'] = coffer['secure_key']
    return coffer['class'](coffer['location'], mode=mode,
        backup=coffer['backup'], **coffer_args)

defconffile = os.path.join(os.path.expanduser("~"), ".pycofferrc")
opt_configuration = click.option('-c', "--conf",
    # ~ type=click.File("rb"),
    help="The pycoffer configuration file.",
    show_default=True,
    default=defconffile
)

defaults = Config.get_defaults(defconffile)

opt_coffer = click.option('-f', "--coffer",
    help='The coffer name.',
    show_default=True,
    default=defaults['coffer'] if 'coffer' in defaults else None
)

