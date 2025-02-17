# -*- encoding: utf-8 -*-
"""Encrypt/Decrypt external files using keys of coffer
"""

__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import datetime

from cofferfile.decorator import reify

from . import CofferPlugin, CliInterface

class Rsync(CofferPlugin, CliInterface):
    desc = "Rsync"

    @classmethod
    @reify
    def _imp_lib_cli(cls):
        """Lazy loader for lib cli"""
        import importlib
        return importlib.import_module('pycoffer.plugins.rsync_cli')

    @classmethod
    def cli(cls):
        """Lazy loader for click"""
        return cls._imp_lib_cli.cli

    def rsync(self, source, target):
        """Encrypt source in target"""
        pass

