# -*- encoding: utf-8 -*-
"""Use FIDO keys as key store
"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

from cofferfile.decorator import reify

from . import AuthPlugin, CliInterface, AuthInterface, ConfigInterface

try:
    from fido2.client import UserInteraction

    class CliInteraction(UserInteraction):
        def __init__(self):
            self._pin = None

        def prompt_up(self):
            print("\nTouch your authenticator device now...\n")

        def request_pin(self, permissions, rd_id):
            if not self._pin:
                from getpass import getpass
                self._pin = getpass("Enter PIN: ")
            return self._pin

        def request_uv(self, permissions, rd_id):
            print("User Verification required.")
            return True

except ImportError:

    class CliInteraction():
        pass

class Fido(AuthPlugin, CliInterface, AuthInterface, ConfigInterface):
    desc = "Use FIDO "

    @classmethod
    @reify
    def _imp_lib_cli(cls):
        """Lazy loader for lib cli"""
        import importlib
        return importlib.import_module('pycoffer.plugins.fido_cli')

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
    def _imp_fido2_ctap(cls):
        """Lazy loader for lib fido2.ctap"""
        import importlib
        return importlib.import_module('fido2.ctap')

    @classmethod
    @reify
    def _imp_fido2_ctap2(cls):
        """Lazy loader for lib fido2.ctap2"""
        import importlib
        return importlib.import_module('fido2.ctap2')

    @classmethod
    @reify
    def _imp_fido2_ctap2_extensions(cls):
        """Lazy loader for lib fido2.ctap2.extensions"""
        import importlib
        return importlib.import_module('fido2.ctap2.extensions')

    @classmethod
    @reify
    def _imp_fido2_ctap2_pin(cls):
        """Lazy loader for lib fido2.ctap2.pin"""
        import importlib
        return importlib.import_module('fido2.ctap2.pin')

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
    @reify
    def _imp_string(cls):
        """Lazy loader for string
        """
        import importlib
        return importlib.import_module('string')

    @classmethod
    def verify_rp_id(self, rp_id: str, origin: str) -> bool:
        """Checks if a Webauthn RP ID is usable for a given origin.

        :param rp_id: The RP ID to validate.
        :param origin: The origin of the request.
        :return: True if the RP ID is usable by the origin, False if not.
        """
        return True

    @classmethod
    def get_rp(cls, rp_id: str = 'pycoffer', rp_name: str = "PyCoffer"):
        """Get local RP.
        """
        return cls._imp_fido2_webauthn.PublicKeyCredentialRpEntity(id=rp_id.encode(), name=rp_name)

    @classmethod
    def get_ident(cls, size=32) -> str:
        """Get string random ident.
        """
        alphabet = self._imp_string.ascii_letters + self._imp_string.digits
        return ''.join(self._imp_secrets.choice(alphabet) for i in range(size))

    @classmethod
    def generate_config(cls, user_ident: str = None, user_name: str = 'pycoffer', user_display_name: str = "PyCoffer keys",
        rp_id: str = None, rp_name: str = "PyCoffer"
    ):
        """Generate configs.
        """
        if user_ident is None:
            user_ident = cls.get_ident(32)
        if rp_id is None:
            rp_id = cls.get_ident(32)
        private = {
            'rp_id': rp_id,
            'rp_name': rp_name,
            'user_ident': user_ident,
            'user_name': user_name,
            'user_display_name': user_display_name,
        }
        cert = {
            'rp_id': rp_id,
            'credential_id': None,
        }
        return private, cert

    @classmethod
    def get_infos(cls, device, **kwargs):
        """Locate a CTAP device suitable for use.

        If running on Windows as non-admin, the predicate check will be skipped and
        a webauthn.dll based client will be returned.

        Extra kwargs will be passed to the constructor of Fido2Client.

        The client will be returned, with the CTAP2 Info, if available.
        """
        ret = {
            'device': '%s'%device,
            'product_name': '%s'%device.product_name,
            'serial_number': '%s'%device.serial_number,
            'usb_id': '%04x:%04x'%(device.descriptor.vid, device.descriptor.pid),
            'path': '%s'%(device.descriptor.path),

        }
        ret['capabilities'] = {
            'WINK': cls._imp_fido2_hid.CAPABILITY(device.capabilities).supported(cls._imp_fido2_hid.CAPABILITY.WINK),
            'LOCK': cls._imp_fido2_hid.CAPABILITY(device.capabilities).supported(cls._imp_fido2_hid.CAPABILITY.LOCK),
            'CBOR': cls._imp_fido2_hid.CAPABILITY(device.capabilities).supported(cls._imp_fido2_hid.CAPABILITY.CBOR),
            'NMSG': cls._imp_fido2_hid.CAPABILITY(device.capabilities).supported(cls._imp_fido2_hid.CAPABILITY.NMSG),
        }

        if device.capabilities & cls._imp_fido2_hid.CAPABILITY.CBOR:
            ctap2 = cls._imp_fido2_ctap2.Ctap2(device)
            ret['info'] = ctap2.get_info()
        else:
            ret['info'] = None
        return ret

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
    def get_devices(cls, extension="hmac-secret"):
        for dev in cls._imp_fido2_hid.CtapHidDevice.list_devices():
            if extension is None:
                yield dev
            else:
                _, info = cls.get_client(dev)
                if extension in info.extensions:
                    yield dev

    @classmethod
    def register(cls, device, user_ident: str = None, user_name: str = 'pycoffer',
        user_display_name: str = "PyCoffer keys", rp_id: str = None, rp_name: str = "PyCoffer",
    ):
        """Register a key and return params as a tuple of dict"""
        private, cert = cls.generate_config(user_ident=user_ident, user_name=user_name,
            user_display_name=user_display_name, rp_id=rp_id, rp_name=rp_name)
        print(private, cert)
        rp = cls.get_rp(rp_id=private['rp_id'], rp_name=private['rp_name'])

        user = cls._imp_fido2_webauthn.PublicKeyCredentialUserEntity(
            id=private['user_ident'].encode(),
            name=private['user_name'],
            display_name=private['user_display_name']
        )

        challenge = cls._imp_secrets.token_bytes(32)

        client, _ = cls.get_client(device, origin=private['rp_id'])

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
        if hasattr(result, 'client_extension_results'):
            client_extension_results = result.client_extension_results
        else:
            client_extension_results = result.extension_results
        if client_extension_results is None or not client_extension_results.get(
            "hmacCreateSecret"
        ):
            raise RuntimeError("Failed to create credential with HmacSecret")

        if hasattr(result, 'attestation_object'):
            attestation_object = result.attestation_object
        else:
            attestation_object = result.response.attestation_object
        if client_extension_results is None or not client_extension_results.get(
            "hmacCreateSecret"
        ):
            raise RuntimeError("Failed to create credential with HmacSecret")
        credential = attestation_object.auth_data.credential_data
        if credential is None:
            raise RuntimeError("Can't get credential with HmacSecret")

        cert['credential_id'] = credential.credential_id

        return private, cert

    @classmethod
    def check(cls, device, cred_id: bytes, rp_id: str):
        """Check we can derive from this device using cred_id and rp_id"""
        salt = cls._imp_secrets.token_bytes(32)
        try:
            key1, key2 = cls.derive_from_credential(device, cred_id=cred_id, rp_id=rp_id, salt1=salt)
            return key1 != None
        except (cls._imp_fido2_ctap.CtapError, cls._imp_fido2_client.ClientError, IndexError):
            return False

    @classmethod
    def derive(cls, device, cred_id, rp_id: str, salt1: bytes, salt2: bytes=None):
        """Derive salts from a list of credentials"""
        if isinstance(cred_id, list) is False:
            cred_id = [cred_id]
        for crid in cred_id:
            try:
                key1, key2 = cls.derive_from_credential(device, cred_id=crid, rp_id=rp_id, salt1=salt1, salt2=salt2)
                return key1, key2
            except (cls._imp_fido2_ctap.CtapError, cls._imp_fido2_client.ClientError, IndexError):
                pass
        raise ValueError("Can't find valid credential in list")

    @classmethod
    def derive_from_credential(cls, device, cred_id: bytes, rp_id: str, salt1: bytes, salt2: bytes=None):
        """Derive salts from a credential"""
        # Prepare parameters for getAssertion
        challenge = cls._imp_secrets.token_bytes(32)
        allow_list = [
            cls._imp_fido2_webauthn.PublicKeyCredentialDescriptor(
                type=cls._imp_fido2_webauthn.PublicKeyCredentialType.PUBLIC_KEY,
                id=cred_id
            )
        ]

        client, _ = cls.get_client(device, origin=rp_id)
        salts = {"salt1": salt1}
        if salt2 is not None:
            salts['salt2'] = salt2

        # Authenticate the credential
        assertion_result = client.get_assertion(
            options=cls._imp_fido2_webauthn.PublicKeyCredentialRequestOptions(
                rp_id=rp_id.encode(),
                challenge=challenge,
                allow_credentials=allow_list,
                extensions={"hmacGetSecret": salts},
            ),
        ).get_response(
            0
        )  # Only one cred in allowList, only one response.

        if hasattr(assertion_result, 'client_extension_results'):
            client_extension_results = assertion_result.client_extension_results
        else:
            client_extension_results = assertion_result.extension_results
        if client_extension_results is None:
            raise RuntimeError("Can't get HmacSecret")
        output1 = client_extension_results["hmacGetSecret"]["output1"]
        output2 = None
        if len(salts) > 1:
            output2 = client_extension_results["hmacGetSecret"]["output2"]
        print(output1, output2)
        return output1, output2

    @classmethod
    def list_rps(cls, device, pin):
        """List all FIDO credentials on your key that have the HMAC_SECRET extension enabled
        experimental
        """
        client, _ = cls.get_client(device)

        print(client.info)
        # Check if credential management is supported
        if "credentialMgmtPreview" not in client.info.options and "credMgmt" not in client.info.options:
            raise TypeError("Key does %s not allow credentialMgmt"%device)

        client_pin = cls._imp_fido2_ctap2_pin.ClientPin(client._backend.ctap2)
        client_token = client_pin.get_pin_token(
            pin,
            cls._imp_fido2_ctap2_pin.ClientPin.PERMISSION.CREDENTIAL_MGMT
        )

        # Initialize credential management
        cred_mgmt = cls._imp_fido2_ctap2.CredentialManagement(
            client._backend.ctap2,
            client_pin.protocol,
            client_token
        )

        # ~ # Get all Relying Parties (RPs)
        # ~ rp_list = cred_mgmt.enumerate_rps()

        # ~ if len(rp_list) == 0:
            # ~ print("No credential RPs found on this Key.")

        # ~ print(f"\nFound {len(rp_list)} Relying Parties with credentials:")

        hmac_creds_count = 0
        total_creds_count = 0

        # Iterate through each RP
        # ~ for rp_index, (_, rp_info) in cred_mgmt.enumerate_rps():
        for rp in cred_mgmt.enumerate_rps():
            print('rp', rp)
            rp_id = rp_info["id"]
            rp_name = rp_info.get("name", rp_id)

            print(f"\n{rp_index+1}. RP: {rp_name} ({rp_id})")

            # Iterate through credentials
            for cred_index, (cred_id, user_info, public_key, cred_info) in cred_mgmt.enumerate_creds(rp_id):
                total_creds_count += 1

                # Extract user info
                user_name = user_info.get("name", "Unknown")
                user_display_name = user_info.get("displayName", user_name)
                user_id_b64 = base64.b64encode(user_info["id"]).decode("utf-8")

                # Check if credential has HMAC_SECRET extension
                extensions = cred_info.get("extensions", {})
                has_hmac = "hmacSecret" in extensions and extensions["hmacSecret"]

                if has_hmac:
                    hmac_creds_count += 1

                # Get creation date if available
                creation_date = "Unknown"
                if "creation_date" in cred_info:
                    timestamp = cred_info["creation_date"]
                    creation_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

                # Format credential ID for display
                cred_id_short = cred_id.hex()[:16] + "..." + cred_id.hex()[-4:]

                print(f"  {rp_index+1}.{cred_index+1}. {user_display_name}")
                print(f"      ID: {cred_id_short}")
                print(f"      User: {user_name}")
                print(f"      User ID: {user_id_b64[:10]}...")
                print(f"      Created: {creation_date}")
                print(f"      HMAC_SECRET: {'✓' if has_hmac else '✗'}")

                # Test HMAC_SECRET functionality if credential has it
                if has_hmac:
                    try:
                        # Create a salt
                        test_salt = b"test_salt_000000000000000000000000"

                        # Get assertion with HMAC_SECRET
                        assertions = client.get_assertion(
                            rp_id,
                            b"challenge",
                            [{"type": "public-key", "id": cred_id}],
                            pin=pin,
                            extensions={"hmacGetSecret": {"salt1": test_salt}}
                        )

                        assertion = assertions.get_response(0)
                        if "hmacGetSecret" in assertion.auth_data.extensions:
                            hmac_secret = assertion.auth_data.extensions["hmacGetSecret"]["output1"]
                            print(f"      HMAC Test: Success (first 8 bytes: {hmac_secret[:8].hex()})")
                        else:
                            print("      HMAC Test: Failed (no extension in response)")

                    except Exception as e:
                        print(f"      HMAC Test: Failed ({str(e)[:50]}...)")

        print(f"\nSummary: Found {total_creds_count} total credentials, {hmac_creds_count} with HMAC_SECRET")

