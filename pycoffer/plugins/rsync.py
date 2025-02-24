# -*- encoding: utf-8 -*-
"""Synchronise files
"""

__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import os
import time
import logging

from cofferfile.decorator import reify

from .. import CofferInfo
from . import CofferPlugin, CliInterface

log = logging.getLogger( __name__ )

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

    def rsync(self, source, target, dry=False):
        """Synchronize source in coffer target"""
        infos = []
        dry_ret = []
        if os.path.isdir(source):
            if target is None:
                target = os.path.basename(source)
                # ~ if len(dirnames) > 1:
                    # ~ target = dirnames[-1]
                # ~ else:
                    # ~ target = ''
            len_root = len(source.split('/'))
            for root, dirs, files in os.walk(source):
                for fname in files:
                    # ~ if root != source:
                        # ~ continue
                    sdir = root.split('/')[len_root:]
                    ssdir = ''
                    if len(sdir) > 0:
                        ssdir = '/'.join(sdir)
                    aname = os.path.join( target, ssdir, fname )
                    sname = os.path.join( source, ssdir, fname )
                    infos.append((sname, CofferInfo(aname, store_path=self.coffer_file.dirpath)))
        else:
            if target is None:
                target = os.path.basename(source)
            if isinstance(target, CofferInfo):
                infos.append((source, target))
            else:
                infos.append((source, CofferInfo(target, store_path=self.coffer_file.dirpath)))

        log.debug("Add file(s) to coffer : %s", infos)

        for fname, finfo in infos:

            file_exists = os.path.isfile(finfo.path)

            if file_exists is True:
                if os.path.getmtime(fname) <= finfo.mtime:
                    if dry is True:
                        dry_ret.append("pass %s"%finfo.name)
                    continue
                else:
                    if dry is True:
                        dry_ret.append("found %s"%finfo.name)
                    else:
                        self.coffer_file.delete_raw(arcinfo=finfo)

            if dry is False:
                if finfo.subdir is not None:
                    os.makedirs(os.path.join(self.coffer_file.dirpath, finfo.subdir), exist_ok=True)

                mtime = os.path.getmtime(fname)
                atime = os.path.getatime(fname)

                with open(fname, 'rb') as ff, self.coffer_file.secure_open(finfo.path, mode='wb', **self.coffer_file.secure_params) as sf:
                    sf.write(ff.read())

                os.utime(finfo.path, (atime, mtime))

                self._modified = True

            dry_ret.append("update %s"%finfo.name)

        if self._modified is True:
            self.coffer_file.dirmtime = time.time_ns()

        return dry_ret
