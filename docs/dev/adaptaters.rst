Adaptaters informations
========================

.. list-table::
   :header-rows: 1

   * - Product name
     - Capabilities
     - Versions
     - Extensions
     - Options
     - Transports
     - Algorithms
     - Certifications
     - Pin uv protocols
     - Max msg size
     - Max creds in list
     - Max cred_id length
     - Max large blob
     - Force pin change
     - Min pin length
     - Max cred blob length
     - Max rpids for min_pin
     - Preferred platform uv attempts
     - UV modality
     - Remaining disc creds
     - Vendor prototype config commands
     - Trade names
   * - | Yubico YubiKey OTP+FIDO+CCID
       | (1050:0407)
       | Firmware : 329473
     - | WINK:True
       | LOCK:False
       | CBOR:True
       | NMSG:False
     - | U2F_V2
       | FIDO_2_0
       | FIDO_2_1_PRE
       | FIDO_2_1
     - | credProtect
       | hmac-secret
       | largeBlobKey
       | credBlob
       | minPinLength
     - | rk:True
       | up:True
       | plat:False
       | alwaysUv:False
       | credMgmt:True
       | authnrCfg:True
       | clientPin:True
       | largeBlobs:True
       | pinUvAuthToken:True
       | setMinPINLength:True
       | makeCredUvNotRqd:True
       | credentialMgmtPreview:True
     - | nfc
       | usb
     - | (alg:-7 type:public-key)
       | (alg:-8 type:public-key)
       | (alg:-35 type:public-key)
     - | 
     - | 2
       | 1
     - | 1280
     - | 8
     - | 128
     - | 4096
     - | False
     - | 4
     - | 32
     - | 1
     - | None
     - | None
     - | 100
     - | 
     - | Yubikey 5 NFC
   * - | ExcelSecu FIDO2 Security Key
       | (1ea8:fc25)
       | Firmware : 256
     - | WINK:True
       | LOCK:False
       | CBOR:True
       | NMSG:False
     - | U2F_V2
       | FIDO_2_0
       | FIDO_2_1
       | FIDO_2_1_PRE
     - | credBlob
       | credProtect
       | hmac-secret
       | largeBlobKey
       | minPinLength
     - | rk:True
       | up:True
       | plat:False
       | alwaysUv:False
       | credMgmt:True
       | authnrCfg:True
       | clientPin:True
       | largeBlobs:True
       | pinUvAuthToken:True
       | setMinPINLength:True
       | makeCredUvNotRqd:True
       | credentialMgmtPreview:True
     - | usb
       | nfc
       | ble
     - | (alg:-7 type:public-key)
       | (alg:-8 type:public-key)
     - | FIDO:1
     - | 2
       | 1
     - | 2048
     - | 8
     - | 96
     - | 2048
     - | False
     - | 4
     - | 32
     - | 6
     - | None
     - | None
     - | 50
     - | 
     - | SpearID FIDO2.fi
   * - | ExcelSecu FIDO2 Security Key
       | (1ea8:fc26)
       | Firmware : None
     - | WINK:True
       | LOCK:False
       | CBOR:True
       | NMSG:False
     - | U2F_V2
       | FIDO_2_0
       | FIDO_2_1_PRE
     - | credProtect
       | hmac-secret
     - | rk:True
       | up:True
       | uv:False
       | plat:False
       | uvToken:False
       | clientPin:True
       | credentialMgmtPreview:True
       | userVerificationMgmtPreview:False
     - | usb
     - | (alg:-7 type:public-key)
     - | 
     - | 1
     - | 2048
     - | 8
     - | 96
     - | None
     - | False
     - | 4
     - | None
     - | 0
     - | None
     - | None
     - | None
     - | 
     - | Thetis FIDO2 BioFP+
   * - | FS ePass FIDO
       | (096e:0853)
       | Firmware : None
     - | WINK:True
       | LOCK:True
       | CBOR:True
       | NMSG:False
     - | U2F_V2
       | FIDO_2_0
       | FIDO_2_1_PRE
     - | credProtect
       | hmac-secret
     - | rk:True
       | up:True
       | plat:False
       | clientPin:True
       | credentialMgmtPreview:True
     - | nfc
       | usb
     - | (alg:-7 type:public-key)
     - | 
     - | 1
     - | 1024
     - | 6
     - | 96
     - | None
     - | False
     - | 4
     - | None
     - | 0
     - | None
     - | None
     - | None
     - | 
     - | FEITIAN ePass FIDO2 NFC
   * - | NEOWAVE NEOWAVE Winkeo FIDO2
       | (1e0d:f1d0)
       | Firmware : None
     - | WINK:True
       | LOCK:False
       | CBOR:True
       | NMSG:False
     - | U2F_V2
       | FIDO_2_0
     - | credProtect
       | hmac-secret
     - | rk:True
       | up:True
       | plat:False
       | clientPin:True
     - | 
     - | 
     - | 
     - | 1
     - | 2048
     - | None
     - | None
     - | None
     - | False
     - | 4
     - | None
     - | 0
     - | None
     - | None
     - | None
     - | 
     - | NEOWAVE Winkeo-A FIDO2

|

Add your adaptater to this list :

- install PyCoffer from github with test dependencies

- launch test_plugin_fido_info

    ..code ::

        ./venv/bin/pytest tests/test_fido.py -k test_plugin_fido_info

- this will generate a new file in docs/dev/adaptaters :

    ..code ::

        ExcelSecu_FIDO2_Security_Key
        FS_ePass_FIDO
        ...
        NEOWAVE_NEOWAVE_Winkeo_FIDO2

- submit this file in a PR
