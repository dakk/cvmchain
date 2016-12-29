# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import time
import logging
import coloredlogs
from uuid import uuid4
from twisted.python import log
from twisted.internet import reactor, protocol
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from .proto import Proto
from .. import config


logger = logging.getLogger ('network')
coloredlogs.install (level='DEBUG')

observer = log.PythonLoggingObserver()
observer.start()


class Factory (protocol.Factory):
	def __init__ (self, chain):
		self.chain = chain
		self.peers = {}

	def buildProtocol (self, addr):
		return Proto (self)
	
	def connect (self, host, port):
		point = TCP4ClientEndpoint(reactor, host, port)
		d = connectProtocol(point, Proto (self))
		d.addCallback (lambda p: logger.info ('Peer connected: %s', str (p)))


class Network:
	def __init__ (self, db, chain):
		self.db = db
		self.chain = chain
		self.factory = Factory (self.chain)
		self.endpoint = TCP4ServerEndpoint (reactor, config.CONF['port'])
		self.endpoint.listen (self.factory)

	# These functions should be callable by the chain
	def requestBlocks (self):
		pass

	def requestTransactions (self):
		pass

	def connect (self, host, port):
		self.factory.connect (host, port)

	def loop (self):
		reactor.run (False)

	def shutdown (self):
		reactor.stop()
		logger.info ('Shutdown completed')
