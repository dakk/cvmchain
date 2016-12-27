import libnacl
import binascii
from base58 import b58encode, b58decode
from . import account

class Block:
    raw = {
        'hash': None,
        'height': None,
        'forger': None,
        'timestamp': None,
        'transactions': None,
        'roothash': None,
        'prev': None
    }

    def __getitem__ (self, key):
        return self.raw [key]

    def __setitem__ (self, key, value):
        self.raw [key] = value

    def _calculateRootHash (self):
        txl = ''
        for tx in self['transactions']:
            txl += tx['hash']
        self['roothash'] = binascii.hexlify (libnacl.crypto_hash_sha256 (txl)).decode ()
        self['hash'] = self._calculateHash ()
        return self['roothash']

    def _calculateHash (self):
        hashableBlock = str (self['prev']) + str (self['height']) + str (self['forger']) + str (self['timestamp']) + str (self['roothash']) + str (self['signature'])
        self['hash'] = binascii.hexlify (libnacl.crypto_hash_sha256 (hashableBlock)).decode ()
        return self['hash']

    def _sign (self, privkey):
        kp = account.KeyPair (privkey)
        signableBlock = str (self['prev']) + str (self['height']) + str (self['forger']) + str (self['timestamp']) + str (self['roothash'])
        self['signature'] = kp.sign (signableBlock)
        self['hash'] = self._calculateHash ()
        return self['signature']

    def _verify (self):
        signableBlock = str (self['prev']) + str (self['height']) + str (self['forger']) + str (self['timestamp']) + str (self['roothash'])
        try:
            account.KeyPair.verify (self['forger'], signableBlock, self['signature'])
            return True
        except:
            return False

    def fromJson (data):
        b = Block ()
        b['prev'] = data['prev']
        b['height'] = data['height']
        b['forger'] = data['forger']
        b['timestamp'] = data['timestamp']
        b['transactions'] = data['transactions']
        b['signature'] = data['signature']

        roothash = b._calculateRootHash ()
        if 'roothash' in data:
            assert (roothash != data['roothash'], 'roothash mismatch')
        b['roothash'] = roothash

        hash = b._calculateHash ()
        if 'hash' in data:
            assert (hash != data['hash'], 'hash mismatch')
        b['hash'] = hash

        if 'signature' in data:
            b['signature'] = data['signature']
            assert (b._verify (), 'wrong signature')

        return b


    def forge (self, privkey, db, mempool):
        pass

    def validate (self, db):
        # Validate against db informations (balances, etc)
        if db:
            pass

        return True

    def toJson (self):
        return self.raw


    