# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from .. import config, consensus
from . import transaction, block

import time
import pymongo
import logging
import coloredlogs
logger = logging.getLogger ('chain')
coloredlogs.install (level='DEBUG')

class Chain:
	def __init__ (self, db):
		self.db = db
		self.mempool = {}

		if self.db.get ('blocks').count () == 0:
			logger.info ('Initializing the chain database...')

			self.db.get ('blocks').create_index([('hash', pymongo.ASCENDING)], unique=True)
			self.db.get ('blocks').create_index([('height', pymongo.ASCENDING)], unique=True)
			self.db.get ('accounts').create_index([('address', pymongo.ASCENDING)], unique=True)
			self.db.get ('transactions').create_index([('hash', pymongo.ASCENDING)], unique=True)

			# Push the genesis block 
			genesisBlock = consensus.genesis[config.CONF['chain']]
			b = block.Block.fromJson (genesisBlock)

			"""if not b.verify ():
				logger.critical ('Invalid genesis block, exiting.')
				sys.exit (0)
			"""
			self.db.get ('blocks').insert_one (b.toJson ())
			logger.info ('Genesis block for %s: %s', config.CONF['chain'], b['hash'])

			# Push the genesis miner amount
			self.db.get ('accounts').insert_one ({
				'address': b['miner'],
				'balance': consensus.reward (0),
				'nonce': 0,
				'mined': consensus.reward (0),
				'sent': 0,
				'received': 0
			})
	
		self.lastblock = {
			'height': self.db.get ('blocks').count () - 1,
			'hash': self.db.get ('blocks').find_one({'height': self.db.get ('blocks').count () - 1 })['hash']
		}

	def _updateHeight (self):
		self.lastblock = {
			'height': self.db.get ('blocks').count () - 1,
			'hash': self.db.get ('blocks').find_one({'height': self.db.get ('blocks').count () - 1 })['hash']
		}
		logger.debug ('Height: %d (%s)', self.lastblock['height'], self.lastblock['hash'])

	def shutdown (self):
		logger.info ('Shutdown completed')

	# Return current height and last block hash
	def getHeight (self):
		return self.lastblock

	# Mine a new block
	def mine (self):
		b = block.Block.fromJson ({
			'prevhash': self.lastblock['hash'],
			'target': 0x0FFFFFF,
			'nonce': 0,
			'height': self.lastblock['height'] + 1,
			'miner': 'A5rr5hr1i4FqrjvfnEFybdSmxeULdRQEb1gBgvrihqYD',
			'transactions': [],
			'time': int (time.time ())
		})
		b._calculateHash ()
		bj = b.toJson ()
		self.pushBlocks ([bj])

	def getBlocks (self, last = None, first = None, hash = None, n = 16):
		#print ('getblocks', last, n)
		blocks = []
		lasthash = ""

		#print (last, n)
		if last != None and n != None:
			l = self.db.get ('blocks').find_one ({'hash': last})
			blocksd = self.db.get ('blocks').find ({ 'height': {'$gte': l['height'] + 1}}, projection={'_id': False}).sort ("height").limit (n)

			for b in blocksd:
				blocks.append (b)

			if len (blocks) != 0:
				lasthash = blocks[-1]['hash']
		
		return { 'blocks': blocks, 'last': lasthash }

	def pushBlocks (self, blocks):
		#print ('pushblocks', blocks)
		#print (blocks)
		for b in blocks:
			bb = block.Block.fromJson (b)
			self.db.get ('blocks').insert_one (bb.toJson ())
		self._updateHeight ()

	def getTransactions (self):
		txs = []
		for hash, tx in dict.iteritems():
			txs.append (tx)

		return txs

	def pushTransactions (self, transactions):
		for txdata in transactions:
			if not txdata['hash'] in self.mempool:
				tx = transaction.Transaction.fromJson (tx)
				if tx.validate (self.db):
					self.mempool [tx.hash] = tx.toJson ()
				else:
					logger.warning ('Received a not valid tx: ', tx.hash)
