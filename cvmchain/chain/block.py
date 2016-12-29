import libnacl
import binascii
from base58 import b58encode, b58decode
from . import account

class Block:
    _raw = {
        'hash': None,
        'height': None,
        'miner': None,
        'timestamp': None,
        'transactions': None,
        'roothash': None,
        'prev': None
    }

    def __getitem__ (self, key):
        return self._raw [key]

    def __setitem__ (self, key, value):
        self._raw [key] = value

    def _calculateRootHash (self):
        txl = ''
        for tx in self['transactions']:
            txl += tx['hash']
        self['roothash'] = binascii.hexlify (libnacl.crypto_hash_sha256 (txl)).decode ()
        self['hash'] = self._calculateHash ()
        return self['roothash']

    def _calculateHash (self):
        hashableBlock = str (self['prev']) + str (self['height']) + str (self['miner']) + str (self['timestamp']) + str (self['roothash'])
        self['hash'] = binascii.hexlify (libnacl.crypto_hash_sha256 (hashableBlock)).decode ()
        return self['hash']

    def fromJson (data):
        b = Block ()
        b['prev'] = data['prev']
        b['height'] = data['height']
        b['miner'] = data['miner']
        b['timestamp'] = data['timestamp']
        b['transactions'] = data['transactions']

        roothash = b._calculateRootHash ()
        if 'roothash' in data:
            assert (roothash != data['roothash'], 'roothash mismatch')
        b['roothash'] = roothash

        hash = b._calculateHash ()
        if 'hash' in data:
            assert (hash != data['hash'], 'hash mismatch')
        b['hash'] = hash

        return b


    def validate (self, db):
        # Validate against db informations (balances, etc)
        if db:
            pass

        return True

    def toJson (self):
        return self._raw


    