# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from .. import config, consensus
from . import transaction, block

import time
import pymongo
import random
import logging
import coloredlogs
from threading import Lock
logger = logging.getLogger ('chain')
coloredlogs.install (level='DEBUG')

class Chain:
	def __init__ (self, db):
		self.db = db
		self.mempool = {}
		self.miner = None
		self.chainLock = Lock ()

		if self.db.get ('blocks').count () == 0:
			logger.info ('Initializing the chain database...')

			self.db.get ('blocks').create_index([('hash', pymongo.ASCENDING)], unique=True)
			self.db.get ('blocks').create_index([('height', pymongo.ASCENDING)], unique=True)
			self.db.get ('accounts').create_index([('address', pymongo.ASCENDING)], unique=True)
			self.db.get ('transactions').create_index([('hash', pymongo.ASCENDING)], unique=True)

			# Push the genesis block 
			genesisBlock = consensus.genesis[config.CONF['chain']]
			b = block.Block.fromJson (genesisBlock)

			self.db.get ('blocks').insert_one (b.toJson ())
			logger.info ('Genesis block for %s: %s', config.CONF['chain'], b.hash)

			# Push the genesis miner amount
			self.db.get ('accounts').insert_one ({
				'address': b.miner,
				'balance': consensus.reward (0),
				'nonce': 0,
				'mined': consensus.reward (0),
				'sent': 0,
				'received': 0
			})

		self.sync = False
		self._updateHeight ()

	def setFactory (self, f):
		self.factory = f

	def _updateHeight (self):
		self.lastblock = self.db.get ('blocks').find_one({'height': self.db.get ('blocks').count () - 1 })

		if self.miner != None and self.miner.height < self.lastblock['height']:
			logger.info ('Updating mining block')
			self.miner.updateLastblock (self.lastblock)

		logger.debug ('Height: %d (%s): %r', self.lastblock['height'], self.lastblock['hash'], self.sync)


	def shutdown (self):
		logger.info ('Shutdown completed')

	# Return current height and last block hash
	def getHeight (self):
		return self.lastblock

	# Mine a new block
	def mine (self, miner):
		while True:
			if not self.sync:
				logger.info ('Node not in sync, waiting for mining')
				time.sleep (15)
				continue

			logger.info ('Starting miner...')
			self.miner = block.BlockMiner (self.lastblock, self.getMempool (), miner)
			self.miner.mine ()
			bj = self.miner.toJson ()
			logger.info ('Mined new block: %s %d', bj['hash'], bj['height'])
			if self.pushBlocks ([bj]) > 0:
				self.factory.broadcastBlock (bj)


	def revertFork (self):
		h = self.getHeight ()

		if h['height'] != 0:
			self.db.get ('blocks').remove ({'height': h['height']})
			logger.info ('Removed last block because of a fork')
			self._updateHeight ()

	def getBlocks (self, last = None, first = None, hash = None, n = 16):
		#print ('getblocks', last, n)
		blocks = []
		lasthash = ""

		#print (last, n)
		if last != None and n != None:
			l = self.db.get ('blocks').find_one ({'hash': last})
			if l == None:
				return {'blocks': [], 'last': ''}
			blocksd = self.db.get ('blocks').find ({ 'height': {'$gte': l['height'] + 1}}, projection={'_id': False}).sort ("height").limit (n)

			for b in blocksd:
				blocks.append (b)

			if len (blocks) != 0:
				lasthash = blocks[-1]['hash']
		
		return { 'blocks': blocks, 'last': lasthash }

	def pushBlocks (self, blocks):
		pushed = 0
		self.chainLock.acquire ()
		for b in blocks:
			bb = block.Block.fromJson (b)

			if bb.prevhash == self.lastblock['hash'] and bb.height == self.lastblock['height'] + 1:
				bbjs = bb.toJson ()
				self.db.get ('blocks').insert_one (bbjs)

				# TODO Update the miner balance

				self.lastblock = bbjs
				self._updateHeight ()
				pushed += 1

		self.chainLock.release ()
		return pushed

	def getMempool (self):
		txs = []
		for hash, tx in self.mempool:
			txs.append (tx)
		
		#sorted (txs, key=hash)
		return txs

	def updateMempool (self, transactions):
		for txdata in transactions:
			if not txdata['hash'] in self.mempool:
				tx = transaction.Transaction.fromJson (tx)
				if tx.validate (self.db):
					self.mempool [tx.hash] = tx.toJson ()
				else:
					logger.warning ('Received a not valid tx: ', tx.hash)
