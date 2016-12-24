import sys
from .network import *

network = Network ()

def main ():
    if sys.argv[1] == '1':
        network.start (8556)
        network.connect ('127.0.0.1', 8556)
        network.loop ()
    else:
        network.start (8557)
        network.connect ('127.0.0.1', 8556)
        network.connect ('127.0.0.1', 8557)
        network.loop ()