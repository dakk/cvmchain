import json
from twisted.internet import protocol, threads

import logging
import coloredlogs
logger = logging.getLogger ('proto')
coloredlogs.install (level='DEBUG')

"""
All chain calls that read or write from disk, should be run in another thread with:

from twisted.internet import reactor, threads

def doLongCalculation():
    # .... do long calculation here ...
    return 3

def printResult(x):
    print x

# run method in thread and get result as defer.Deferred
d = threads.deferToThread(doLongCalculation)
d.addCallback(printResult)
reactor.run()

http://twistedmatrix.com/documents/11.0.0/core/howto/threading.html

Thread safety will be implemented in chain with locks
"""

class Proto (protocol.Protocol):
	def __init__ (self, factory):
		self.factory = factory
		self.nodeid = self.factory.nodeid
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
		logger.debug ('Data received: %s', data)
		data = data.decode()

		for line in data.splitlines ():
			line = line.strip ()
			m = json.loads (line)

			if m['type'] in self.messageHandlers:
				logger.debug ('New message: %s', m['type'])
				self.messageHandlers [m['type']] (data)
			else:
				logger.warning ('Unhandled message: %s', m['type'])

	def sendData (self, m):
		logger.debug ('Send data: %s', str (m))
		data = json.dumps (m)
		self.transport.write (bytes (data.encode ()) + b'\n')

	def connectionMade(self):
		remote_ip = self.transport.getPeer()
		host_ip = self.transport.getHost()
		self.remote_ip = remote_ip.host + ":" + str (remote_ip.port)
		self.host_ip = host_ip.host + ":" + str (host_ip.port)
		logger.debug ("Connection from %s", self.transport.getPeer())

	def connectionLost(self, reason):
		#if self.remote_nodeid in self.factory.peers:
		#	self.factory.peers.pop(self.remote_nodeid)
		#	self.lc_ping.stop()
		logger.debug ("Disconnected")
			

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
		self.sendPing ()

	# Get the list of all connected peers
	def getPeers (self, m):
		pass

	# List of peers
	def peers (self, m):
		pass

	def getHeight (self, m):
		self.sendHeight (self.factory.chain.getHeight ())

	def height (self, m):
		pass

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
	def sendHello (self, software, version, chain, height):
		self.sendData ({'type': 'hello', 'software': software, 'version': version, 'chain': chain, 'height': height})

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