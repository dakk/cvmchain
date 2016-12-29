# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import coloredlogs
from pymongo import MongoClient
from . import config

logger = logging.getLogger ('database')
coloredlogs.install (level='DEBUG')

class Database:
	def __init__ (self):
		self.client = MongoClient (config.CONF['db']['host'], config.CONF['db']['port'])
		self.db = self.client [config.CONF['db']['database']]
		logger.info ('Connected to mongodb %s:%d/%s', config.CONF['db']['host'], config.CONF['db']['port'], config.CONF['db']['database'])

	def get (self, collection = None):
		if collection:
			return self.db[collection]
		else:
			return self.db

	def shutdown (self):
		logger.info ('Shutdown completed')