# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import os
import json
import signal
import getopt
import logging
import coloredlogs
from twisted.internet import protocol, threads, task

from .network import *
from .chain import *
from . import config, database

logger = logging.getLogger ('main')
coloredlogs.install (level='DEBUG')


def signal_handler (sig, frame):
	global network, db, chain
	logger.info ('Exiting...')
	network.shutdown ()
	chain.shutdown ()
	db.shutdown ()


def usage ():
	print ('Usage:', sys.argv[0], '[OPTIONS]\n')
	print ('Mandatory arguments:')
	print ('\t-h,--help\t\t\tdisplay this help')
	print ('\t-V,--version\t\t\tdisplay the software version')
	print ('\t-v,--verbose=n\t\t\tset verbosity level to n=[1-5]')
	print ('\t-D,--data=path\t\t\tspecify a custom data directory path (default: ' + config.DATA_DIR+')')
	print ('\t-d,--daemon\t\t\trun the software as daemon')
	print ('\t-c,--chain=chainname\t\tblock-chain', '[' + (', '.join (map (lambda x: "'"+x+"'", config.CHAINS))) + ']')
	print ('\t-p,--port=port\t\t\tdht port')
	print ('\t--db=dbname\t\t\tname of the db')
	print ('\t--api-port=port\t\t\tset an api port')
	print ('\t-s,--seed=host:port,[host:port]\tset a nodes list')
	print ('\t--mine\tset a nodes list')


def main ():
	logger.info ('%s %s', config.APP_NAME, config.APP_VERSION)

	# Argument recognition
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hv:VD:c:spd", ["mine", "help", "verbose=", "version", "data=", "daemon", "chain=", "api-port=", "api=", "seed=", "port=", "db="])
	except getopt.GetoptError:
		usage ()
		sys.exit (2)


	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage ()
			sys.exit ()

		elif opt in ("-V", "--version"):
			sys.exit ()

		elif opt in ("-D", "--data"):
			config.DATA_DIR = os.path.expanduser (arg)

		elif opt in ("-v", "--verbose"):
			config.VERBOSE = int (arg)

		elif opt in ("-d", "--daemon"):
			logger.critical ('Daemon is not yet implemented')
			sys.exit ()

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

	# Overrides	
	mine = False
	for opt, arg in opts:
		if opt in ("--db"):
			config.CONF['db']['database'] = arg
		elif opt in ("-c", "--chain"):
			config.CONF['chain'] = arg
		elif opt in ("-s", "--seed"):
			for n in arg.split (','):
				config.CONF['nodes'].append ({'host': n.split (':')[0], 'port': int (n.split (':')[1])})
		elif opt in ("-p", "--port"):
			config.CONF['port'] = int (arg)
		elif opt in ("--api-port"):
			config.CONF['api']['port'] = int (arg)
		elif opt in ("--mine"):
			mine = True

	# Bind signals
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGQUIT, signal_handler)

	# Start the mainloop
	global network, db, chain

	db = database.Database ()
	chain = Chain (db)
	#chain.mine ()		
	network = Network (db, chain)

	for node in config.CONF['nodes']:
		network.connect (node['host'], node['port'])

	if mine:
		timer = task.LoopingCall (lambda: chain.mine ())
		timer.start (7.0)

	network.loop ()