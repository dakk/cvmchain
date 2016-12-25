import sys
import time
from uuid import uuid4
from twisted.internet import reactor, protocol
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol

from .proto import Proto
from .. import config

import logging
import coloredlogs
logger = logging.getLogger ('network')
coloredlogs.install (level='DEBUG')

from twisted.python import log
observer = log.PythonLoggingObserver()
observer.start()


class Factory (protocol.Factory):
	def __init__ (self, chain):
		self.chain = chain
		self.peers = {}

	def buildProtocol (self, addr):
		return Proto (self)


class Network:
	def __init__ (self, db, chain):
		self.db = db
		self.chain = chain
		self.factory = Factory (self.chain)
		self.endpoint = TCP4ServerEndpoint (reactor, config.CONF['port'])
		self.endpoint.listen (self.factory)

	def connect (self, host, port):
		point = TCP4ClientEndpoint(reactor, host, port)
		d = connectProtocol(point, Proto (self.factory))
		d.addCallback (lambda p: logger.info ('Peer connected: %s', str (p)))

	def loop (self):
		reactor.run (False)

	def shutdown (self):
		reactor.stop()
		logger.info ('Shutdown completed')
