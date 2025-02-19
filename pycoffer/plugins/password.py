# -*- encoding: utf-8 -*-
"""Store passswords in coffer

"""

__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import datetime

from cofferfile.decorator import reify

from . import FilePlugin, PluginInfo, CliInterface


class PasswordInfoPublic(PluginInfo):

    def __init__(self, name=None, username=None, password=None, url=None, note=None, owner=None, **kwargs):
        """Helper for passowrd public info"""
        super().__init__(name=name, **kwargs)
        self.username = username
        self.url = url
        self.note = note
        self.owner = owner


class PasswordInfo(PasswordInfoPublic):

    def __init__(self, name=None, username=None, password=None, url=None, note=None, owner=None, **kwargs):
        """Helper for passowrd info"""
        super().__init__(name=name, username=username, url=url, note=note, owner=owner, **kwargs)
        self.password = password

    def to_public(self):
        """Remove sensible data"""
        return PasswordInfoPublic(name=self.name, username=self.username, url=self.url, note=self.note, owner=self.owner)


class Password(FilePlugin, CliInterface):
    desc = "Manage password in coffer"
    arcname = '.plugins/passwd'

    def __init__(self):
        super().__init__()
        self.store = {
        }

    @classmethod
    @reify
    def _imp_lib_cli(cls):
        """Lazy loader for lib cli"""
        import importlib
        return importlib.import_module('pycoffer.plugins.password_cli')

    @classmethod
    def cli(cls):
        """Lazy loader for click"""
        return cls._imp_lib_cli.cli

    @classmethod
    @reify
    def _imp_lib_csv(cls):
        """Lazy loader for lib csv"""
        import importlib
        return importlib.import_module('csv')

    @classmethod
    @property
    def Info(cls):
        """Factory for Info"""
        return PasswordInfo

    def store_load(self, data):
        """Load data from store in coffer"""
        if data is not None:
            self.store = data
        self._modified = False

    def store_dump(self):
        """Dump data in store in coffer"""
        self._modified = False
        return self.store

    def getmembers(self):
        """List public data about passwords in coffer"""
        ret = []
        for k in self.store.keys():
            ret.append(PasswordInfoPublic(**self.store[k].to_dict()))
        return ret

    def add(self, datainfo=None, replace=True):
        """Add or replace info in store"""
        if isinstance(datainfo, PasswordInfo) is False:
            raise ValueError("Need a PasswordInfo")
        if replace is False and (datainfo.owner, datainfo.name) in self.store:
            raise IndexError("Data already exist %s,%s"%(datainfo.owner, datainfo.name))
        self.store[datainfo.owner, datainfo.name] = datainfo
        self._modified = True

    def delete(self, datainfo=None):
        """"Delete data at key"""
        if isinstance(datainfo, PasswordInfoPublic) is False:
            raise ValueError("Need a PasswordInfoPublic")
        del self.store[datainfo.owner, datainfo.name]
        self._modified = True

    def get(self, key):
        """Get data for key"""
        if isinstance(key, PasswordInfo) is True:
            key = key.owner, key.name
        return self.store[key]

    def import_chrome(self, filename, replace=True):
        """Import chrome passwords from filename"""
        with open(filename) as csv_file:
            csv_reader = self._imp_lib_csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    if row[0].upper() != 'NAME':
                        raise ValueError('Wanted column %s but found %s' % ("name", row[0]))
                    if row[1].upper() != 'URL':
                        raise ValueError('Wanted column %s but found %s' % ("url", row[1]))
                    if row[2].upper() != 'USERNAME':
                        raise ValueError('Wanted column %s but found %s' % ("username", row[2]))
                    if row[3].upper() != 'PASSWORD':
                        raise ValueError('Wanted column %s but found %s' % ("password", row[3]))
                    if row[4].upper() != 'NOTE':
                        raise ValueError('Wanted column %s but found %s' % ("note", row[4]))
                    line_count += 1
                else:
                    pinfo = PasswordInfo(name=row[0], username=row[2],
                        url=row[1], password=row[3], note=row[4],
                        owner='chrome', mtime=datetime.datetime.now())
                    self.add(datainfo=pinfo, replace=replace)
                    line_count += 1

