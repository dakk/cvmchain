import sys
from uuid import uuid4
from twisted.python import log
from twisted.internet import reactor, protocol
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol

from .proto import Proto

class Factory (protocol.Factory):
	def startFactory (self):
		self.peers = {}
		self.nodeid = uuid4 ()

	def buildProtocol (self, addr):
		return Proto (self)


def gotPeer (p):
	print ('Got peer', p)
	p.sendHello (0, 0, 0, 0)


class Network:
	def start (self, port):
		log.startLogging (sys.stdout)
		endpoint = TCP4ServerEndpoint (reactor, port)
		endpoint.listen (Factory ())

	def connect (self, host, port):
		point = TCP4ClientEndpoint(reactor, host, port)
		f = Factory ()
		f.startFactory ()
		d = connectProtocol(point, Proto (f))
		d.addCallback (gotPeer)

	def loop (self):
		reactor.run ()