# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import libnacl
import binascii
import time
from base58 import b58encode, b58decode
from ..crypto import hash

class Block:
	def __init__ (self, hash=None, prevhash=None, roothash=None, height=None, \
			miner=None, time=None, transactions=None, nonce=None, target=None):
		self.__hash = hash
		self.__prevhash = prevhash
		self.__roothash = roothash
		self.__height = height
		self.__miner = miner
		self.__time = time
		self.__transactions = transactions
		self.__nonce = nonce
		self.__target = target


	##### Hash
	@property
	def hash (self):
		return self.__hash

	##### Prevhash
	@property
	def prevhash (self):
		return self.__prevhash
	
	@prevhash.setter
	def prevhash (self, value):
		self.__prevhash = value

	##### Roothash
	@property
	def roothash (self):
		return self.__roothash
	

	##### Height
	@property
	def height (self):
		return self.__height
	
	@height.setter
	def height (self, value):
		self.__height = value

	##### Miner
	@property
	def miner (self):
		return self.__miner
	
	@miner.setter
	def miner (self, value):
		self.__miner = value

	##### Time
	@property
	def time (self):
		return self.__time
	
	@time.setter
	def time (self, value):
		self.__time = value

	##### Transactions
	@property
	def transactions (self):
		return self.__transactions
	
	@transactions.setter
	def transactions (self, value):
		self.__transactions = value

	##### Nonce
	@property
	def nonce (self):
		return self.__nonce

	@nonce.setter
	def nonce (self, value):
		self.__nonce = value

	##### Target
	@property
	def target (self):
		return self.__target

	@target.setter
	def target (self, value):
		self.__target = value


	##### Methods
	def _calculateRootHash (self):
		txl = list (map (lambda tx: tx.hash, self.transactions))
		txl.sort ()			

		self.__roothash = hash.merkle (txl)
		self._calculateHash ()
		return self.roothash

	def _calculateHash (self):
		hashableBlock = str (self.prevhash) + str (self.roothash) + str (self.height) + \
			str (self.miner) + str (self.time) + str (self.target) + str (self.nonce)

		self.__hash = hash.dsha256 (hashableBlock)
		return self.hash


	def checkTarget (self):
		self._calculateHash ()
		if int (self.hash, 16) > (int (self.target, 16) * 2 ** (8 * (0x1d - 3))): 
			return False
		else:
			return True


	# Used for importing a block from other peers
	def fromJson (data):
		b = Block (prevhash=data['prevhash'], height=data['height'], miner=data['miner'], \
			time=data['time'], target=data['target'], nonce=data['nonce'], transactions=data['transactions'])

		# Check hash
		roothash = b._calculateRootHash ()
		if 'roothash' in data and roothash != data['roothash']:
			raise BaseException ('roothash mismatch')
	
		# Check roothash
		hash = b._calculateHash ()
		if 'hash' in data and hash != data['hash']:
			raise BaseException ('hash mismatch')

		# Check target
		if not b.checkTarget ():
			raise BaseException ('target mismatch')

		return b




	def validate (self, db):
		# Validate against db informations (balances, etc)
		if db:
			pass

		return True

	def toJson (self):
		return {
			'hash': self.__hash,
			'prevhash': self.__prevhash,
			'roothash': self.__roothash,
			'height': self.__height,
			'miner': self.__miner,
			'time': self.__time,
			'transactions': self.__transactions,
			'nonce': self.__nonce,
			'target': self.__target
		}



class BlockMiner (Block):
	def __init__ (self, lastblock, mempool, miner):
		super ().__init__ (prevhash=lastblock['hash'], target=lastblock['target'], nonce=0, \
			height=lastblock['height'] + 1, miner=miner, transactions=mempool, time=int (time.time ()))
		self._calculateRootHash ()

	def mine (self):
		while not self.checkTarget ():
			self.nonce += 1
