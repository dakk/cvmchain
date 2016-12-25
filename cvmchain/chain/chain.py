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
		return 0