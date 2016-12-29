# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from base58 import b58encode, b58decode
from base64 import b64encode, b64decode
import binascii
import libnacl.public
import libnacl.sign
import libnacl.encode

class Signer:
    _pair = None

    def __init__ (self, privateKey = None):
        if privateKey == None:
            self._pair = libnacl.sign.Signer()
        else:
            self._pair = libnacl.sign.Signer(seed=b58decode (privateKey))

    def publicKey (self):
        return b58encode (self._pair.vk)

    def privateKey (self):
        return b58encode (self._pair.seed)

    def toJson (self):
        return {
            'public': self.publicKey (),
            'private': self.privateKey ()
        }

    def sign (self, data):
        return b64encode (self._pair.signature (data.encode ())).decode ()

    def verify (self, data, signature):
        verifier = libnacl.sign.Verifier (self._pair.vk)
        return verifier.verify (sn + data.encode ())


class Verifier:
    def __init__ (self, publicKey):
        self._pk = libnacl.encode.hex_encode (b58decode (publicKey))

    def verify (self, data, signature):
        sn = b64decode (signature.encode ())
        verifier = libnacl.sign.Verifier (self._pk)
        return verifier.verify (sn + data.encode ())

    