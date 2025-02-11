# -*- encoding: utf-8 -*-
"""CLI programm

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import os
import configparser

class Config():

    def __init__(self, filename, chkmode=True):
        self.filename = filename
        self.parser = configparser.ConfigParser()
        self.parser.read(filename)

        # ~ config.sections()

        # ~ config.sections()

        # ~ 'forge.example' in config

        # ~ 'python.org' in config

        # ~ config['forge.example']['User']

        # ~ config['DEFAULT']['Compression']

        # ~ topsecret = config['topsecret.server.example']
        # ~ topsecret['ForwardX11']

        # ~ topsecret['Port']

        # ~ for key in config['forge.example']:
            # ~ print(key)

    def check_perms(self, exc=True):
        mode = oct(os.stat(self.filename).st_mode)[-3:]
        if mode != '600':
            if exc is True:
                raise PermissionError('File %s must be user read/write only: 600 != %s !!!'%(self.filename, mode))
            else:
                return False
        else:
            return True
