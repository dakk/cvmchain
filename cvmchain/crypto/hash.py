# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import hashlib
import binascii
from base58 import b58encode, b58decode


def balloon (data):
	return '0x00000000000000000000'

def sha256 (data):
	m = hashlib.sha256 ()
	m.update (data.encode ())
	return binascii.hexlify (m.digest ()).decode ()

def dsha256 (data):
	return sha256 (sha256 (data))

def merkle (leaves):
	if len (leaves) == 0:
		return sha256 ('')

	if len (leaves) == 1:
		return leaves [0]

	nleaves = []
	for i in range (0, len (leaves), 2):
		if i+1 < len (leaves):
			nleaves.append (sha256 (leaves[i] + leaves[i+1]))
		else:
			nleaves.append (sha256 (leaves[i]))
	
	merkle (nleaves)
