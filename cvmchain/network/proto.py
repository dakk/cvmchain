import json
from twisted.internet import protocol


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
		data = data.decode()

		for line in data.splitlines ():
			line = line.strip ()
			m = json.loads (line)

			if m['type'] in self.messageHandlers:
				print ('New message:', m['type'])
				self.messageHandlers [m['type']] (data)
			else:
				print ('Unhandled message:', m['type'])

	def sendData (self, m):
		data = json.dumps (m)
		self.transport.write (bytes (data.encode ()) + b'\n')

	def connectionMade(self):
		remote_ip = self.transport.getPeer()
		host_ip = self.transport.getHost()
		self.remote_ip = remote_ip.host + ":" + str(remote_ip.port)
		self.host_ip = host_ip.host + ":" + str(host_ip.port)
		print ("Connection from", self.transport.getPeer())

	def connectionLost(self, reason):
		#if self.remote_nodeid in self.factory.peers:
		#	self.factory.peers.pop(self.remote_nodeid)
		#	self.lc_ping.stop()
		print (self.nodeid, "disconnected")
			

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
		pass

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
	def sendHello (self, sname, sversion, chain, height):
		print ('Sending hello...')
		self.sendData ({'type': 'hello'})

	def sendPing (self):
		self.sendData ({'type': 'ping'})

	def sendPong (self):
		self.sendData ({'type': 'pong'})

	def sendGetPeers (self):
		pass

	def sendPeers (self, peers):
		pass

	def sendGetHeight (self):
		pass

	def sendHeight (self, height):
		pass

	def sendGetBlocks (self, blast):
		pass

	def sendBlocks (self, blocks):
		pass

	def sendGetTransactions (self):
		pass

	def sendTransactions (self, transactions):
		pass