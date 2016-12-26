from pymongo import MongoClient
from .. import config

import logging
import coloredlogs
logger = logging.getLogger ('chain')
coloredlogs.install (level='DEBUG')

class Chain:
	def __init__ (self, db):
		self.db = db

	def shutdown (self):
		logger.info ('Shutdown completed')

	# Should be get last block?
	def getHeight (self):
		return self.db.get ()['blocks'].count () + 1, '0x001'

	def getBlocks (self, last = None, first = None, hash = None, n = 16):
		return [], ''

	def getTransactions (self):
		return []

	def pushBlocks (self, blocks):
		pass

	def pushTransactions (self, transactions):
		pass