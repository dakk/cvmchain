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
		self.chain.setFactory (self)
		self.peers = {}
		self.peerIds = []
		self.nodeid = str (uuid4 ())
		self.sync = False

		self.timer = task.LoopingCall (lambda: self.forkLoop ())
		self.timer.start (5.0)		

		self.lastbroadcasted = None

	def broadcastBlock (self, block):
		if self.lastbroadcasted != None and self.lastbroadcasted['hash'] == block['hash']:
			return

		self.lastbroadcasted = block

		for p in self.peers:
			if self.peers[p]['last'] != block['hash'] and self.peers[p]['height'] < block['height']:
				self.peers[p]['proto'].sendBlock (block)

	def forkLoop (self):
		commonHeights = {}
		maxh = (0, 0, None)

		for peer in self.peers:
			if not self.peers[peer]['connected'] or self.peers[peer]['blocksreceived'] != 0:
				continue

			last = self.peers [peer]['last']
			h = self.peers [peer]['height']

			if not last in commonHeights:
				commonHeights [last] = { 'n': 1, 'peers': [peer] }
			else:
				commonHeights [last]['peers'].append (peer)
				commonHeights [last]['n'] += 1

			if commonHeights [last]['n'] > maxh[0]:
				maxh = (commonHeights [last]['n'], h, last)

		if maxh[0] < 1:
			self.chain.setSync (True)
			return

		h = self.chain.getHeight ()

		if maxh[1] == h['height'] and maxh[2] == h['hash']:
			self.chain.setSync (True)
		elif maxh[1] > h['height']:
			self.chain.setSync (False)

		if maxh[2] != h['hash'] and maxh[1] >= h['height']:
			logger.error ('Possible fork detected: %s %d common for %d peers: %s', maxh[2], maxh[1], maxh[0], str (commonHeights [maxh[2]]['peers']))
			self.chain.revertFork ()

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
