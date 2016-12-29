# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import libnacl
import binascii
from base58 import b58encode, b58decode

class Block:
    _raw = {
        'hash': None,

        'prevhash': None,
        'roothash': None,
        'height': None,
        'miner': None,
        'time': None,
        'target': None,
        'nonce': None,

        'transactions': None,
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
        hashableBlock = str (self['prevhash']) + str (self['roothash']) + str (self['height']) + str (self['miner']) + str (self['time']) + str (self['target']) + str (self['nonce'])
        self['hash'] = binascii.hexlify (libnacl.crypto_hash_sha256 (hashableBlock)).decode ()
        return self['hash']

    def fromJson (data):
        b = Block ()
        b['prevhash'] = data['prevhash']
        b['height'] = data['height']
        b['miner'] = data['miner']
        b['time'] = data['time']
        b['target'] = data['target']
        b['nonce'] = data['nonce']
        b['transactions'] = data['transactions']

        # Check hash
        roothash = b._calculateRootHash ()
        if 'roothash' in data:
            assert (roothash != data['roothash'], 'roothash mismatch')
        b['roothash'] = roothash
    
        # Check roothash
        hash = b._calculateHash ()
        if 'hash' in data:
            assert (hash != data['hash'], 'hash mismatch')
        b['hash'] = hash

        # Check target

        return b


    def validate (self, db):
        # Validate against db informations (balances, etc)
        if db:
            pass

        return True

    def toJson (self):
        return self._raw


    