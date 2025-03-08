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
    import yaml
    conf = Config.generate('test', type='null', location=os.path.join(tmpdir.name, 'test.coffer'))
    conffile = os.path.join(tmpdir.name, 'test.conf')
    with open(conffile, 'wt') as f:
        yaml.safe_dump(conf, f)

    yield conffile

    tmpdir.cleanup()

@pytest.fixture
def fido():
    """Return a random string that can be used as filename"""
    import fido2.ctap2
    import fido2.client
    from . import fido2_emulator

    device = fido2_emulator.VirtualCtapDevice()

    # Create CTAP2 client
    ctap2 = fido2.ctap2.Ctap2(device, strict_cbor=False)

    # ~ oldCtap2 = fido2.ctap2.base.Ctap2
    # ~ fido2.ctap2.base.Ctap2 = MockCtap2
    # ~ fido2.ctap2.Ctap2 = MockCtap2
    # ~ fido2.client.Ctap2 = MockCtap2

    yield device, ctap2

    # ~ fido2.ctap2.base.Ctap2 = oldCtap2
    # ~ fido2.ctap2.Ctap2 = oldCtap2
    # ~ fido2.client.Ctap2 = oldCtap2


