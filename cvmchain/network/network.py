# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import time
import logging
import coloredlogs
from uuid import uuid4
from twisted.python import log
from twisted.internet import reactor, protocol, task
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

		self.timer = task.LoopingCall (lambda: self.forkLoop ())
		self.timer.start (1.0)

	def forkLoop (self):
		commonHeights = {}
		maxh = (0, None)

		for peer in self.peers:
			last = self.peers [peer]['last']
			if not last in commonHeights:
				commonHeights [last] = { 'n': 1, 'peers': [peer] }
			else:
				commonHeights [last]['peers'].append (peer)
				commonHeights [last]['n'] += 1

			if commonHeights [last]['n'] > maxh[0]:
				maxh = (commonHeights [last]['n'], last)

		#print (commonHeights)
		#print (maxh)
		if maxh[0] < 2:
			return

		h = self.chain.getHeight ()['hash']
		if maxh[1] != h:
			logger.error ('Possible fork detected: %s common for %d peers: %s', maxh[1], maxh[0], str (commonHeights [maxh[1]]['peers']))

	def buildProtocol (self, addr):
		return Proto (self)
	
	def peerConnected (self, p):
		logger.info ('Peer connected: %s', str (p))

	def connect (self, host, port):
		point = TCP4ClientEndpoint(reactor, host, port)
		d = connectProtocol(point, Proto (self))
		d.addCallback (lambda p: self.peerConnected (p))


class Network:
	def __init__ (self, db, chain):
		self.db = db
		self.chain = chain
		self.factory = Factory (self.chain)
		self.endpoint = TCP4ServerEndpoint (reactor, config.CONF['port'])
		self.endpoint.listen (self.factory)

	def connect (self, host, port):
		self.factory.connect (host, port)

	def loop (self):
		reactor.run (False)

	def shutdown (self):
		reactor.stop()
		logger.info ('Shutdown completed')
