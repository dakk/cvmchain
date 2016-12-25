import sys
import os
import json

from .network import *
from .chain import *
from . import config

import logging
import coloredlogs
logger = logging.getLogger ('main')
coloredlogs.install (level='DEBUG')

def main ():
	logger.info ('%s %s', config.APP_NAME, config.APP_VERSION)

	# Data directory check
	firstrun = False

	if not os.path.isdir (config.DATA_DIR):
		logger.warning ('Directory %s not present', config.DATA_DIR)
		os.mkdir (config.DATA_DIR)
		logger.info ('Directory %s created', config.DATA_DIR)
		firstrun = True

	if not os.path.isdir (config.DATA_DIR+'/testnet/'):
		logger.warning ('Directory %s not present', config.DATA_DIR+'/testnet')
		os.mkdir (config.DATA_DIR+'/testnet')
		logger.info ('Directory %s created', config.DATA_DIR+'/testnet')
		firstrun = True

	# Config creation
	if not os.path.exists(config.DATA_DIR+'/'+config.APP_NAME+'.json'):
		logger.warning ('Configuration file %s not present', config.DATA_DIR+'/'+config.APP_NAME+'.json')
		f = open (config.DATA_DIR+'/'+config.APP_NAME+'.json', 'w')
		f.write (json.dumps (config.CONF, indent=4, separators=(',', ': ')))
		f.close ()
		logger.info ('Configuration file %s created', config.DATA_DIR+'/'+config.APP_NAME+'.json')
		firstrun = True

	# Load config file
	f = open (config.DATA_DIR+'/'+config.APP_NAME+'.json', 'r')
	conf = f.read ()
	f.close ()

	config.CONF = json.loads (conf)
	logger.info ('Configuration file %s loaded', config.DATA_DIR+'/'+config.APP_NAME+'.json')


	# Start the network
	chain = Chain ()
	network = Network (8556, chain)
	network.connect ('127.0.0.1', 8556)
		
	network.loop ()