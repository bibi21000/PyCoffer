# -*- encoding: utf-8 -*-
"""Encrypt/Decrypt external files using keys of coffer
"""

__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

from cofferfile.decorator import reify

from . import OtherPlugin, CliInterface

class Crypt(OtherPlugin, CliInterface):
    desc = "Encrypt/ decrypt external files with key's coffer"

    @classmethod
    @reify
    def _imp_lib_cli(cls):
        """Lazy loader for lib cli"""
        import importlib
        return importlib.import_module('pycoffer.plugins.crypt_cli')

    @classmethod
    def cli(cls):
        """Lazy loader for click"""
        return cls._imp_lib_cli.cli

    def encrypt(self, source, target):
        """Encrypt source in target"""
        with open(source, "rb") as src, self.crypt_open(target, 'wb') as tgt:
            tgt.write(src.read())

    def decrypt(self, source, target):
        """Decrypt source in target"""
        with open(target, "wb") as tgt, self.crypt_open(source, 'rb') as src:
            tgt.write(src.read())

