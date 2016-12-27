from .. import config, consensus
from . import transaction, block

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

			self.db.get ('blocks').insert_one (b.toJson ())
			logger.info ('Genesis block for %s: %s', config.CONF['chain'], b['hash'])

			# Push the genesis forger amount
			self.db.get ('accounts').insert_one ({
				'address': b['forger'],
				'balance': consensus.genesis_reward,
				'nonce': 0,
				'forged': consensus.genesis_reward,
				'sent': 0,
				'received': 0
			})			

	def shutdown (self):
		logger.info ('Shutdown completed')

	# Should be get last block?
	def getHeight (self):
		height = self.db.get ('blocks').count () - 1
		hash = self.db.get ('blocks').find_one({'height': height })['hash']
		return height, hash

	def getBlocks (self, last = None, first = None, hash = None, n = 16):
		return [], ''

	def pushBlocks (self, blocks):
		pass

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
