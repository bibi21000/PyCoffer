# -*- encoding: utf-8 -*-
"""PyCoffer plugins

"""

__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import sys
import datetime

from cofferfile.decorator import reify


class PluginInfo():
    """Data used with plugin. Better to use class than free data"""

    def __init__(self, name=None, ctime=None, mtime=None):
        """Helper for passowrd info"""
        self.name = name
        if ctime is None:
            self.ctime = datetime.datetime.now()
        else:
            self.ctime = ctime
        if mtime is None:
            self.mtime = datetime.datetime.now()
        else:
            self.mtime = mtime

    def to_dict(self):
        """Convert to dict"""
        return vars(self)

    def __repr__(self):
        """"""
        if hasattr(self, 'name'):
            s = self.name
        else:
            s = 'Unknown'
        return '<PluginInfo ' + s + ' ' + hex(id(self)) + '>'

class Plugin():
    category = None
    desc = "Description"

    @classmethod
    @reify
    def _imp_metadata(cls):
        """Lazy loader for metadata"""
        import importlib
        if sys.version_info < (3, 10):
            return importlib.import_module('importlib_metadata')
        else:
            return importlib.import_module('importlib.metadata')

    @classmethod
    def collect(cls, name=None, group="cofferfile.plugin"):
        """Collect plugins"""
        eps = cls._imp_metadata.entry_points()
        grps = []
        for grp in eps.groups:
            if grp.startswith(group) is False:
                continue
            grps.append(grp)

        plugins = []
        for grp in grps:
            eps = cls._imp_metadata.entry_points(group=grp)
            for ep in eps:
                if name is not None:
                    if ep.name != name:
                        continue
                plugins.append(ep.load())

        return plugins

    @classmethod
    def collect_cli(cls, group="cofferfile.plugin"):
        """Collect plugins with cli interface"""
        return [ plg for plg in cls.collect(group=group) if issubclass(plg, CliInterface)]

    @classmethod
    @property
    def Info(cls):
        """Factory for Info data"""
        return PluginInfo

class OtherPlugin(Plugin):
    category = 'other'

class FilePlugin(Plugin):
    category = 'file'

    def __init__(self):
        self._modified = False

    @property
    def modified(self):
        return self._modified

    def store_dump(self, data):
        return None

    def store_load(self, data):
        self._modified = False

class CliInterface():

    @classmethod
    def cli(cls):
        """Lazy loader for cli"""
        raise RuntimeError("Not defined")
