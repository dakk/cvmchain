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

	def getHeight (self):
		return self.db.get ()['blocks'].count () + 1

	def getBlocks (self, istart, iend):
		return []

	def getTransactions (self):
		return []

	def pushBlocks (self, blocks):
		pass

	def pushTransactions (self, transactions):
		pass