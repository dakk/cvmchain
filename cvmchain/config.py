# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import os

APP_NAME = 'cvmchain'
APP_VERSION = 0.1
AUTHOR = 'Davide Gessa'
AUTHOR_EMAIL = 'gessadavide@gmail.com'

def app_data_path (appname, roaming=True):
	if sys.platform.startswith('java'):
		os_name = platform.java_ver()[3][0]
		if os_name.startswith('Windows'):
			system = 'win32'
		elif os_name.startswith('Mac'):
			system = 'darwin'
		else:
			system = 'linux2'
	else:
		system = sys.platform

	if system == "win32":
		const = roaming and "CSIDL_APPDATA" or "CSIDL_LOCAL_APPDATA"
		path = os.path.normpath(_get_win_folder(const))
		if appname:
			path = os.path.join(path, appname)
	elif system == 'darwin':
		path = os.path.expanduser('~/Library/Application Support/')
		if appname:
			path = os.path.join(path, appname)
	else:
		path = os.getenv('XDG_DATA_HOME', os.path.expanduser("~/"))
		if appname:
			path = os.path.join(path, '.'+appname)
	return path


VERBOSE = 1
DATA_DIR = app_data_path (appname=APP_NAME)
CHAINS = ['mainnet', 'testnet']

CONF = {
	'chain': 'testnet',
	'port': 6187,

	'api': {
		'port': 8080
	},

	'db': {
		'host': 'localhost',
		'port': 27017,
		'credentials': '',
		'database': "cvmchain"
	},

	'nodes': [
		#{ 'host': 'localhost', 'port': 3030 }
	]
}