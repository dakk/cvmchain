# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from setuptools import find_packages
from setuptools import setup
from cvmchain import config

setup(name='cvmchain',
	version=config.APP_VERSION,
	description='',
	author='Davide Gessa',
	setup_requires='setuptools',
	author_email='gessadavide@gmail.com',
	packages=['cvmchain', 'cvmchain.network', 'cvmchain.chain'],
	entry_points={
		'console_scripts': [
			'cvmchain=cvmchain.cvmchain:main',
		],
	},
	install_requires=open ('requirements.txt', 'r').read ().split ('\n')
)
