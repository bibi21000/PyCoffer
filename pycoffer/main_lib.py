# -*- encoding: utf-8 -*-
""" pyfernet main script.

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import os
import click

def open_coffer(conf, store, mode):
    from .config import Config
    confcoff = Config(conf, chkmode=True)
    coffer = confcoff.coffer(store)
    return coffer['class'](coffer['location'], mode=mode,
        coffer_key=coffer['coffer_key'], secure_key=coffer['secure_key'],
        backup=coffer['backup'])

opt_configuration = click.option('-c', "--conf",
    # ~ type=click.File("rb"),
    help="The pycoffer configuration file",
    default=os.path.join(os.path.expanduser("~"), ".pycofferrc")
)

opt_store = click.option('-s', "--store",
    help='The store name'
)

