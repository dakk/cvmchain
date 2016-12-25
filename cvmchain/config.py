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



DATA_DIR = app_data_path (appname=APP_NAME)

CONF = {
	'chain': 'testnet',
	'port': 6797,

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
		{ 'host': 'localhost', 'port': 3030, 'ssl': False }
	]
}