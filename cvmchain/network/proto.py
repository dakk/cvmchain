import random
import json
import datetime
from .. import config
from twisted.internet import protocol, threads, task

import logging
import coloredlogs
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

			'getTransactions': self.getTransactions,
			'transactions': self.transactions
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

		self.factory.peers [self.remoteIp] = {
			'connected': True,
			'height': None,
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

	# Get the list of all connected peers
	def getPeers (self, m):
		pass

	# List of peers
	def peers (self, m):
		pass

	def getHeight (self, m):
		d = threads.deferToThread (self.factory.chain.getHeight)
		d.addCallback (lambda height: self.sendHeight (height))

	def height (self, m):
		self.factory.peers [self.remoteIp]['height'] = m['height']

	def getBlocks (self, m):
		pass

	def blocks (self, m):
		pass

	def getTransactions (self, m):
		pass

	def transactions (self, m):
		pass


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
		self.sendData ({'type': 'height', 'peers': peers})

	def sendGetHeight (self):
		self.sendData ({'type': 'getHeight'})

	def sendHeight (self, height):
		self.sendData ({'type': 'height', 'height': height})

	def sendGetBlocks (self, last):
		self.sendData ({'type': 'getBlocks', 'last': last})

	def sendBlocks (self, blocks):
		self.sendData ({'type': 'blocks', 'blocks': blocks})

	def sendGetTransactions (self):
		self.sendData ({'type': 'getTransactions'})

	def sendTransactions (self, transactions):
		self.sendData ({'type': 'transactions', 'transactions': transactions})