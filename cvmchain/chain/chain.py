import time
from pymongo import MongoClient

import logging
import coloredlogs
logger = logging.getLogger ('chain')
coloredlogs.install (level='DEBUG')

class Chain:
    def __init__ (self):
        self.client = MongoClient ('localhost', 27017)
        self.db = self.client ['cvmchain']
        logger.info ('Connected to mongodb')

    # Close all leveldb databases
    def shutdown (self):
        pass

    def getHeight (self):
        return 0