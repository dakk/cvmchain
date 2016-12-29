# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import libnacl
import binascii
from base58 import b58encode, b58decode

class Hash:
    def balloon (data):
        return '0x00000000000000000000'

    def sha256 (data):
        return binascii.hexlify (libnacl.crypto_hash_sha256 (data)).decode ()