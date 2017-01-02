# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import time
import logging
import random
import coloredlogs
from uuid import uuid4
from twisted.python import log
from twisted.internet import reactor, protocol, task
from threading import Lock
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from .proto import Proto
from .. import config


logger = logging.getLogger ('network')
coloredlogs.install (level='DEBUG')

observer = log.PythonLoggingObserver()
observer.start()

class PeerList:
	def __init__ (self):
		self.__list = {}
		self.__ids = []

	def add (self, remoteIp, peer):
		self.__ids.append (peer['nodeid'])
		self.__list [remoteIp] = peer

	def __getitem__(self, remoteIp):
		if remoteIp in self.__list:
			return self.__list [remoteIp]
		else:
			return None

	def resetBlocksReceived (self, remoteIp):
		if remoteIp in self.__list:
			self.__list [remoteIp]['blocksreceived'] = 0

	def subBlocksReceived (self, remoteIp):
		if remoteIp in self.__list:
			self.__list [remoteIp]['blocksreceived'] -= 1

	def updateLastMessage (self, remoteIp, lastmessage):
		if remoteIp in self.__list:
			self.__list [remoteIp]['lastmessage'] = lastmessage

	def updateHeight (self, remoteIp, height, last):
		if remoteIp in self.__list:
			self.__list [remoteIp]['height'] = height
			self.__list [remoteIp]['last'] = last

	def disconnect (self, remoteIp):
		if remoteIp in self.__list:
			self.__list [remoteIp]['connected'] = False
			self.__ids.remove (self.__list [remoteIp]['nodeid'])

	def exists (self, nodeid):
		return nodeid in self.__ids or nodeid in self.__list

	def toList (self, connected=True):
		return list (filter (lambda v: v['connected'] == connected, list (self.__list.values ())))


class Factory (protocol.Factory):
	def __init__ (self, chain):
		self.chain = chain
		self.chain.setFactory (self)
		self.peers = PeerList ()
		self.nodeid = str (uuid4 ())
		self.sync = False

		self.timer = task.LoopingCall (lambda: self.syncLoop ())
		self.timer.start (1)	


	def broadcastBlock (self, block):
		for p in self.peers.toList ():
			if p['last'] != block['hash'] and p['height'] < block['height']:
				p['proto'].sendBlock (block)


	def syncLoop (self):
		commonHeights = {}
		maxh = (0, 0, None)

		for p in self.peers.toList ():
			last = p['last']
			h = p['height']

			if not last in commonHeights:
				commonHeights [last] = { 'n': 1, 'peers': [p] }
			else:
				commonHeights [last]['peers'].append (p)
				commonHeights [last]['n'] += 1

			if commonHeights [last]['n'] > maxh[0]:
				maxh = (commonHeights [last]['n'], h, last, commonHeights [last]['peers'])

		if maxh[0] < 1:
			self.chain.sync =True
			return

		h = self.chain.getHeight ()

		if maxh[1] == h['height'] and maxh[2] == h['hash']:
			self.chain.sync = True
		elif maxh[1] > h['height']:
			self.chain.sync = False
			logger.debug ('Synching...')
			
			proto = (random.choice (maxh[3]))['proto']
			proto.sendGetBlocks (last=h['hash'], n=128)
			
		if (random.choice (maxh[3]))['blocksreceived'] < -2 and maxh[2] != h['hash'] and maxh[1] >= h['height']:
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
