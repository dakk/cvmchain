# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import random
import json
import datetime
import logging
import coloredlogs
from twisted.internet import protocol, threads, task
from .. import config

logger = logging.getLogger ('proto')
coloredlogs.install (level='DEBUG')

class Proto (protocol.Protocol):
	def __init__ (self, factory):
		self.factory = factory
		self.messageHandlers = {
			'hello': self.hello,
			'ping': self.ping,
			'pong': self.pong,
			'getHeight': self.getHeight,
			'height': self.height,
			'getPeers': self.getPeers,
			'peers': self.peers,
			'getBlocks': self.getBlocks,
			'blocks': self.blocks,
			'getMempool': self.getMempool,
			'mempool': self.mempool
		}

	def dataReceived (self, data):
		#logger.debug ('Data received: %s', data)
		data = data.decode()

		for line in data.splitlines ():
			line = line.strip ()
			try:
				m = json.loads (line)
			except:
				logger.error ('Unparsable message')
				continue

			if m['type'] in self.messageHandlers:
				self.factory.peers [self.remoteIp]['lastmessage'] = datetime.datetime.utcnow ()
				logger.info ('New message: %s', m['type'])
				self.messageHandlers [m['type']] (m)
			else:
				logger.warning ('Unhandled message: %s', m['type'])

	def sendData (self, m):
		logger.debug ('Send message: %s', str (m['type']))
		data = json.dumps (m)
		self.transport.write (bytes (data.encode ()) + b'\n')

	def connectionMade (self):
		remote = self.transport.getPeer()
		host = self.transport.getHost()
		self.remoteIp = remote.host + ":" + str (remote.port)
		self.hostIp = host.host + ":" + str (host.port)

		#print (self.remoteIp, self.hostIp)

		self.factory.peers [self.remoteIp] = {
			'host': remote.host,
			'port': remote.port,
			'connected': True,
			'height': None,
			'last': None,
			'software': None,
			'version': None,
			'lastmessage': datetime.datetime.utcnow ()
		}

		logger.info ("Connection from %s", self.transport.getPeer())
		self.sendHello (config.APP_NAME, config.APP_VERSION, config.CONF['chain'])

		self.timer = task.LoopingCall (lambda: self.timerLoop ())
		self.timer.start (1.0)

	def timerLoop (self):
		diff = datetime.datetime.utcnow () - self.factory.peers [self.remoteIp]['lastmessage']

		if diff > datetime.timedelta (seconds=random.randint (45,75)): 
			self.sendPing ()
		if diff > datetime.timedelta (seconds=random.randint (5,10)): 
			self.sendGetHeight ()
		if diff > datetime.timedelta (minutes=15):
			pass 
			
	def connectionLost(self, reason):
		self.timer.stop ()
		self.factory.peers [self.remoteIp]['connected'] = False
		logger.info ("Disconnected")
			

	###################
	# Message handlers

	# Ping a node
	def ping (self, m):
		self.sendPong ()

	# Response to a ping
	def pong (self, m):
		pass

	# Send the hello message
	def hello (self, m):
		self.factory.peers [self.remoteIp]['software'] = m['software']
		self.factory.peers [self.remoteIp]['version'] = m['version']

		self.sendGetHeight ()
		self.sendPing ()
		self.sendGetPeers ()

	# Get the list of all connected peers
	def getPeers (self, m):
		l = []
		for x in self.factory.peers:
			if self.factory.peers [x]['connected'] and (self.factory.peers[x]['host'] + ':' + str(self.factory.peers[x]['port'])) != self.hostIp: 
				l.append ({ 'host': self.factory.peers [x]['host'], 'port': self.factory.peers [x]['port'] })
		self.sendPeers (l)

	# List of peers
	def peers (self, m):
		#print (m)
		# Perform a bootstrap
		for peer in m['peers']:
			if (peer['host'] + ':' + str(peer['port'])) != self.hostIp and not (peer['host'] + ':' + str (peer['port'])) in self.factory.peers: 
				self.factory.connect (peer['host'], peer['port'])

	def getHeight (self, m):
		d = threads.deferToThread (self.factory.chain.getHeight)
		d.addCallback (lambda res: self.sendHeight (res['height'], res['hash']))

	def height (self, m):
		self.factory.peers [self.remoteIp]['height'] = m['height']
		self.factory.peers [self.remoteIp]['last'] = m['last']

		height = self.factory.chain.getHeight ()

		if m['height'] > height['height']:
			self.sendGetBlocks (last=height['hash'], n=16)

		#print (m)

	def getBlocks (self, m):
		if 'last' in m and 'n' in m:
			d = threads.deferToThread (self.factory.chain.getBlocks, last=m['last'], n=m['n'])
		elif 'first' in m and 'n' in m:
			d = threads.deferToThread (self.factory.chain.getBlocks, first=m['first'], n=m['n'])
		elif 'hash':
			d = threads.deferToThread (self.factory.chain.getBlocks, hash=m['hash'])
		d.addCallback (lambda res: self.sendBlocks (res['blocks'], res['last']))

	def blocks (self, m):
		threads.deferToThread (self.factory.chain.pushBlocks, m['blocks'])


	def getMempool (self, m):
		d = threads.deferToThread (self.factory.chain.getMempool)
		d.addCallback (lambda transactions: self.sendMempool (transactions))

	def mempool (self, m):
		threads.deferToThread (self.factory.chain.updateMempool, m['transactions'])




	###################
	# Message factory
	def sendHello (self, software, version, chain):
		self.sendData ({'type': 'hello', 'software': software, 'version': version, 'chain': chain})

	def sendPing (self):
		self.sendData ({'type': 'ping'})

	def sendPong (self):
		self.sendData ({'type': 'pong'})

	def sendGetPeers (self):
		self.sendData ({'type': 'getPeers'})

	def sendPeers (self, peers):
		self.sendData ({'type': 'peers', 'peers': peers})

	def sendGetHeight (self):
		self.sendData ({'type': 'getHeight'})

	def sendHeight (self, height, last):
		self.sendData ({'type': 'height', 'height': height, 'last': last})

	def sendGetBlocks (self, last = None, first = None, hash = None, n = 16):
		if hash != None:
			self.sendData ({'type': 'getBlocks', 'hash': last})
		elif first != None and n != None:
			self.sendData ({'type': 'getBlocks', 'first': first, 'n': n})
		elif last != None and n != None:
			self.sendData ({'type': 'getBlocks', 'last': last, 'n': n})

	def sendBlocks (self, blocks, last):
		self.sendData ({'type': 'blocks', 'blocks': blocks, 'last': last})

	def sendGetMempool (self):
		self.sendData ({'type': 'getMempool'})

	def sendMempool (self, transactions):
		self.sendData ({'type': 'mempool', 'transactions': transactions})