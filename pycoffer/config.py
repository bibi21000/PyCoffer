# -*- encoding: utf-8 -*-
"""Config lib

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import os
import sys
# ~ import configparser

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points  # noqa
else:
    from importlib.metadata import entry_points  # noqa

from cofferfile.decorator import reify

class Config():

    def __init__(self, filename, chkmode=True):
        self.filename = filename
        # ~ self.parser = configparser.ConfigParser()
        # ~ self.parser.read(filename)
        with open(filename, 'r') as f:
            self.parser = self._imp_yaml.safe_load(f)

    @classmethod
    @reify
    def _imp_yaml(cls):
        """Lazy loader for yaml"""
        import importlib
        return importlib.import_module('yaml')

    def check_perms(self, exc=True):
        """Check user right on config file. Must be 600 !!!"""
        mode = oct(os.stat(self.filename).st_mode)[-3:]
        if mode != '600':
            if exc is True:
                raise PermissionError('File %s must be user read/write only: 600 != %s !!!'%(self.filename, mode))
            else:
                return False
        else:
            return True

    def get_defaults(self, filename=None):
        """Return defaults from configuration file"""
        return self._get_defaults(self.parser)

    @classmethod
    def _get_defaults(self, parser=None):
        """Return defaults from configuration file"""
        ret = {}
        if parser is not None:
            if 'DEFAULT' in ret:
                ret = parser['DEFAULT']
            ret = {}
        if 'ext' not in ret:
            ret['ext'] = '.pcof'
        if 'auth' not in ret:
            ret['auth'] = 'file'
        return ret

    @classmethod
    def Defaults(cls, filename=None):
        """Return defaults from configuration file"""
        if filename is None or os.path.isfile(filename) is False:
            parser = {}
        else:
            with open(filename, 'r') as f:
                parser = cls._imp_yaml.safe_load(f)
        return cls._get_defaults(parser)

    def coffer(self, section=None):
        """Return a coffer matching section"""
        ret = {}
        if section is None:
            section = 'DEFAULT'

        name = ret['type'] = self.parser[section]['type']
        if 'backup' in self.parser[section]:
            ret['backup'] = self.parser[section]['backup']
        else:
            ret['backup'] = None
        if 'auth' in self.parser[section]:
            ret['auth'] = self.parser[section]['auth']
        else:
            ret['auth'] = 'file'
        if ret['auth'] == 'file':
            if 'coffer_key' in self.parser[section]:
                ret['coffer_key'] = self.parser[section]['coffer_key']
                # ~ ret['coffer_key'] = self.parser[section]['coffer_key']
            # ~ else:
                # ~ ret['coffer_key'] = None
            if 'secure_key' in self.parser[section]:
                # ~ ret['secure_key'] = self.parser[section]['secure_key']
                ret['secure_key'] = self.parser[section]['secure_key']
            # ~ else:
                # ~ ret['secure_key'] = None
        else:
            for k in self.parser[section]:
                if k.startswith("%s_"%ret['auth']):
                    ret[k] = self.parser[section][k]
        if 'location' in self.parser[section]:
            if os.path.isdir(self.parser[section]['location']):
                ret['location'] = os.path.join(self.parser[section]['location'], '.'+section)
            else:
                ret['location'] = self.parser[section]['location']
        else:
            if section == 'DEFAULT':
                ret['location'] = os.path.expanduser('~/.pycoffer')
            ret['location'] = '.' + section
        if name is None:
            raise ValueError("coffer_type must be defined for %s"%(section))
        else:
            crpt = entry_points(group='cofferfile.coffer', name=name)
            if len(crpt) != 1:
                raise IndexError("Problem loading %s : found %s matches"%(name, len(crpt)))
            cls = tuple(crpt)[0].load()
            ret['class'] = cls
        return ret

    @classmethod
    def generate(self, coffer_name=None, type=None, location=None, auth='file', backup=None, filename=None):
        """Return a coffer configuration as a list of lines"""
        if coffer_name is None:
            raise ValueError("Youd need to provide a coffer_name")
        # are we called from the class or from instance
        if hasattr(self, 'parser'):
            # From instance, we can use parser
            defaults = self._get_defaults(self.parser)
        else:
            # From class ... if we have filename, we could load defaults
            if filename is None:
                parser = {}
            else:
                with open(filename, 'r') as f:
                    parser = self._imp_yaml.safe_load(f)
            defaults = self._get_defaults(parser)

        if type is None:
            if 'type' in defaults:
                type = defaults['type']
            else:
                raise ValueError("Youd need to provide a type")
        crpt = entry_points(group='cofferfile.coffer', name=type)
        if len(crpt) != 1:
            raise IndexError("Problem loading %s : found %s matches"%(type, len(crpt)))
        cls = tuple(crpt)[0].load()
        ret = {coffer_name : {}}
        ret[coffer_name]['name'] = coffer_name
        ret[coffer_name]['type'] = type
        ret[coffer_name]['auth'] = auth
        if backup is not None:
            ret[coffer_name]['backup'] = backup
        keys = cls.gen_params()
        for k in keys:
            ret[coffer_name][k] = keys[k]
            # ~ ret.append('%s = %s' % (k, keys[k].decode()))
        if location is not None:
            ret[coffer_name]['location'] = location
        elif 'location' in defaults:
            ret[coffer_name]['location'] = defaults['location']
        return ret
