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
