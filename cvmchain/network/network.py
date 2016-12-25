import sys
from uuid import uuid4
from twisted.internet import reactor, protocol
from twisted.python import log
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol

from .proto import Proto

#log.startLogging (sys.stdout)

class Factory (protocol.Factory):
	def __init__ (self):
		self.peers = {}
		self.nodeid = uuid4 ()

	def buildProtocol (self, addr):
		return Proto (self)


def gotPeer (p):
	print ('Got peer', p)
	p.sendHello (0, 0, 0, 0)


class Network:
	def __init__ (self, port, chain):
		self.chain = chain
		self.factory = Factory ()
		self.endpoint = TCP4ServerEndpoint (reactor, port)
		self.endpoint.listen (self.factory)

	def connect (self, host, port):
		point = TCP4ClientEndpoint(reactor, host, port)
		d = connectProtocol(point, Proto (self.factory))
		d.addCallback (gotPeer)

	def loop (self):
		reactor.run (False)