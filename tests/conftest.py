# -*- encoding: utf-8 -*-
import pytest


@pytest.fixture
def random_path():
    """Create and return temporary directory"""
    import tempfile
    tmpdir = tempfile.TemporaryDirectory()
    yield tmpdir.name
    tmpdir.cleanup()

@pytest.fixture
def random_name():
    """Return a random string that can be used as filename"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@pytest.fixture
def coffer_conf():
    """Return a test coffer null in a random place and its configuration file"""
    import os
    import tempfile
    tmpdir = tempfile.TemporaryDirectory()
    from pycoffer.config import Config
    conf = Config.generate('test', type='null', location=os.path.join(tmpdir.name, 'test.coffer'))
    conffile = os.path.join(tmpdir.name, 'test.conf')
    with open(conffile, 'wt') as f:
        for li in conf:
            f.write(li + '\n')

    yield conffile

    tmpdir.cleanup()
