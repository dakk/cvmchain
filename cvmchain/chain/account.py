from base58 import b58encode, b58decode
from base64 import b64encode, b64decode
import binascii
import libnacl.public
import libnacl.sign
import libnacl.encode

class KeyPair:
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

    def verify (publicKey, data, signature):
        pk = libnacl.encode.hex_encode (b58decode (publicKey))
        sn = b64decode (signature.encode ())
        verifier = libnacl.sign.Verifier (pk)
        return verifier.verify (sn + data.encode ())