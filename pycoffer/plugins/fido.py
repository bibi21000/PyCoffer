# -*- encoding: utf-8 -*-
"""Encrypt/Decrypt external files using keys of coffer
"""

__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

from getpass import getpass

# ~ from fido2.server import Fido2Server
# ~ from fido2.utils import websafe_encode, websafe_decode
# ~ import sys
# ~ from fido2.hid import CtapHidDevice
# ~ from fido2.client import Fido2Client, UserInteraction
# ~ from getpass import getpass
# ~ import ctypes
# ~ from fido2.hid import CtapHidDevice, CAPABILITY
# ~ from fido2.ctap2 import Ctap2
# ~ from fido2.ctap2.extensions import HmacSecretExtension
# ~ from fido2.ctap import CtapError
# ~ from fido2.ctap2.pin import ClientPin
# ~ from fido2.ctap2.credman import CredentialManagement
# ~ from fido2.client import Fido2Client
# ~ from fido2.hid import DiscoverableHIDDevice
# ~ from fido2.ctap2 import CredentialManagement
# ~ from fido2.pcsc import CtapPcscDevice

from cofferfile.decorator import reify

from . import OtherPlugin, CliInterface

try:
    from fido2.client import UserInteraction

    class CliInteraction(UserInteraction):
        def __init__(self):
            self._pin = None

        def prompt_up(self):
            print("\nTouch your authenticator device now...\n")

        def request_pin(self, permissions, rd_id):
            if not self._pin:
                self._pin = getpass("Enter PIN: ")
            return self._pin

        def request_uv(self, permissions, rd_id):
            print("User Verification required.")
            return True

except ImportError:

    class CliInteraction():
        pass

class Fido(OtherPlugin, CliInterface):
    desc = "Use FIDO "

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

    @classmethod
    @reify
    def _imp_fido2_hid(cls):
        """Lazy loader for lib fido2.hid"""
        import importlib
        return importlib.import_module('fido2.hid')

    @classmethod
    @reify
    def _imp_fido2_client(cls):
        """Lazy loader for lib fido2.client"""
        import importlib
        return importlib.import_module('fido2.client')

    @classmethod
    @reify
    def _imp_fido2_server(cls):
        """Lazy loader for lib fido2.server"""
        import importlib
        return importlib.import_module('fido2.server')

    @classmethod
    @reify
    def _imp_fido2_ctap2_extensions(cls):
        """Lazy loader for lib fido2.ctap2.extensions"""
        import importlib
        return importlib.import_module('fido2.ctap2.extensions')

    @classmethod
    @reify
    def _imp_fido2_webauthn(cls):
        """Lazy loader for lib fido2.webauthn"""
        import importlib
        return importlib.import_module('fido2.webauthn')

    @classmethod
    @reify
    def _imp_fido2_cose(cls):
        """Lazy loader for lib fido2.cose"""
        import importlib
        return importlib.import_module('fido2.cose')

    @classmethod
    @reify
    def _imp_secrets(cls):
        """Lazy loader for secrets
        """
        import importlib
        return importlib.import_module('secrets')

    @classmethod
    def verify_rp_id(self, rp_id: str, origin: str) -> bool:
        """Checks if a Webauthn RP ID is usable for a given origin.

        :param rp_id: The RP ID to validate.
        :param origin: The origin of the request.
        :return: True if the RP ID is usable by the origin, False if not.
        """
        return True

    @classmethod
    def get_rp(cls, app: str = 'pycoffer', app_name: str = "PyCoffer") -> bool:
        """Get local RP.
        """
        return cls._imp_fido2_webauthn.PublicKeyCredentialRpEntity(id=app, name=app_name)

    @classmethod
    def get_client(cls, device, origin='local', **kwargs):
        """Locate a CTAP device suitable for use.

        If running on Windows as non-admin, the predicate check will be skipped and
        a webauthn.dll based client will be returned.

        Extra kwargs will be passed to the constructor of Fido2Client.

        The client will be returned, with the CTAP2 Info, if available.
        """
        user_interaction = kwargs.pop("user_interaction", None) or CliInteraction()

        client = cls._imp_fido2_client.Fido2Client(
            device=device,
            origin=origin,
            verify=cls.verify_rp_id,
            user_interaction=user_interaction,
            extensions=[cls._imp_fido2_ctap2_extensions.HmacSecretExtension(allow_hmac_secret=True)],
            **kwargs,
        )
        return client, client.info

    @classmethod
    def get_devices(cls):
        for dev in cls._imp_fido2_hid.CtapHidDevice.list_devices():
            _, info = cls.get_client(dev)
            if "hmac-secret" in info.extensions:
                yield dev

    @classmethod
    def register(cls, device, ident=None, name='coffer', display_name=None, app='pycoffer', app_name="PyCoffer"):
        """Generate params for a new store : keys, ... as a dict"""
        rp = cls.get_rp(app=app, app_name=app_name)

        if ident is None:
            ident = cls._imp_secrets.token_bytes(32)
        user = cls._imp_fido2_webauthn.PublicKeyCredentialUserEntity(
            id=ident,
            name=name,
            display_name=display_name
        )

        challenge = cls._imp_secrets.token_bytes(32)

        client, _ = cls.get_client(device, origin=app)

        result = client.make_credential(
            cls._imp_fido2_webauthn.PublicKeyCredentialCreationOptions(
                rp=rp,
                user=user,
                challenge=challenge,
                pub_key_cred_params=[
                    cls._imp_fido2_webauthn.PublicKeyCredentialParameters(
                        type=cls._imp_fido2_webauthn.PublicKeyCredentialType.PUBLIC_KEY,
                        alg=cls._imp_fido2_cose.ES256.ALGORITHM
                    )
                ],
                extensions={"hmacCreateSecret": True},
            ),
        )

        # HmacSecret result:
        if result.extension_results is None or not result.extension_results.get(
            "hmacCreateSecret"
        ):
            raise RuntimeError("Failed to create credential with HmacSecret")

        credential = result.attestation_object.auth_data.credential_data
        if credential is None:
            raise RuntimeError("Can't get credential with HmacSecret")

        return ident, credential.credential_id

    @classmethod
    def derive(cls, device, ident, salt1, salt2=None, app='pycoffer', app_name="PyCoffer"):
        """Generate params for a new store : keys, ... as a dict"""
        # Prepare parameters for getAssertion
        challenge = cls._imp_secrets.token_bytes(32)
        allow_list = [
            cls._imp_fido2_webauthn.PublicKeyCredentialDescriptor(
                type=cls._imp_fido2_webauthn.PublicKeyCredentialType.PUBLIC_KEY,
                id=ident
            )
        ]

        client, _ = cls.get_client(device, origin=app)
        salts = {"salt1": salt1}
        if salt2 is not None:
            salts['salt2'] = salt2

        rp = cls.get_rp(app=app, app_name=app_name)
        # Authenticate the credential
        assertion_result = client.get_assertion(
            options=cls._imp_fido2_webauthn.PublicKeyCredentialRequestOptions(
                rp_id=rp.id,
                challenge=challenge,
                allow_credentials=allow_list,
                extensions={"hmacGetSecret": salts},
            ),
        ).get_response(
            0
        )  # Only one cred in allowList, only one response.

        if assertion_result.extension_results is None:
            raise RuntimeError("Can't get HmacSecret")
        output1 = assertion_result.extension_results["hmacGetSecret"]["output1"]
        output2 = None
        if len(salts) > 1:
            output2 = assertion_result.extension_results["hmacGetSecret"]["output2"]

        return output1, output2
