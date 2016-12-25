import sys
import os
import json

from .network import *
from .chain import *
from . import config



def main ():
	# Data directory check
	firstrun = False

	if not os.path.isdir (config.DATA_DIR):
		print ('Directory %s not present', config.DATA_DIR)
		os.mkdir (config.DATA_DIR)
		print ('Directory %s created', config.DATA_DIR)
		firstrun = True

	if not os.path.isdir (config.DATA_DIR+'/testnet/'):
		print ('Directory %s not present', config.DATA_DIR+'/testnet')
		os.mkdir (config.DATA_DIR+'/testnet')
		print ('Directory %s created', config.DATA_DIR+'/testnet')
		firstrun = True

	# Config creation
	if not os.path.exists(config.DATA_DIR+'/'+config.APP_NAME+'.json'):
		print ('Configuration file %s not present', config.DATA_DIR+'/'+config.APP_NAME+'.json')
		f = open (config.DATA_DIR+'/'+config.APP_NAME+'.json', 'w')
		f.write (json.dumps (config.CONF, indent=4, separators=(',', ': ')))
		f.close ()
		print ('Configuration file %s created', config.DATA_DIR+'/'+config.APP_NAME+'.json')
		firstrun = True

	# Load config file
	f = open (config.DATA_DIR+'/'+config.APP_NAME+'.json', 'r')
	conf = f.read ()
	f.close ()

	config.CONF = json.loads (conf)
	print ('Configuration file %s loaded', config.DATA_DIR+'/'+config.APP_NAME+'.json')


	# Start the network
	if sys.argv[1] == '1':
		network = Network (8556)
		network.connect ('127.0.0.1', 8556)
		network.loop ()
	else:
		chain = Chain ()
		network = Network (chain)
		network.connect ('127.0.0.1', 8556)
		network.connect ('127.0.0.1', 8557)
		
		network.loop ()