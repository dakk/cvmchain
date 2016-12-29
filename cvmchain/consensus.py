# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Genesis block
genesis = {
	'testnet': {
		"hash": "15ee70aa4e615268f44034f9527c21b9e060a462c61d21d65eea59990ccc55f0",
		"prevhash": "0000000000000000000000000000000000000000000000000000000000000000",
		"height": 0,
		"miner": "A5rr5hr1i4FqrjvfnEFybdSmxeULdRQEb1gBgvrihqYD",
		"time": 1482796800,
		"transactions": [],
		"target": 0x0FFFFFF,
		"nonce": 12543,
		"roothash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
	},
	'mainnet': {
		"hash": "",
		"height": 0,
		"miner": "",
		"time": 1482796800,
		"transactios": []
	}
}

genesis_target = 0x0FFFFFFF
retarget = 2048
blocktime = 30

def reward (height):
	if height == 0:
		return 8192 * 100000000
	elif height > 0 and height <= 2048 * 2048:
		return 2 * 100000000
	elif height > 2048 * 2048 and height <= 8 * 2048 * 2048:
		return 1 * 100000000
	else:
		return 0.5 * 100000000
