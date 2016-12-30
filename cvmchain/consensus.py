# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Genesis block
genesis = {
	'testnet': {
		"hash": "0000007a79ddf8144ca8ad634053a7eaa74b0d34d67c2f70834191ef652ac587",
		"prevhash": "0000000000000000000000000000000000000000000000000000000000000000",
		"height": 0,
		"miner": "A5rr5hr1i4FqrjvfnEFybdSmxeULdRQEb1gBgvrihqYD",
		"time": 1483098543,
		"transactions": [],
		"target": "09FFFFFF",
		"nonce": 1601136,
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
maxtxinblock = 1024

def reward (height):
	if height == 0:
		return 8192 * 100000000
	elif height > 0 and height <= 2048 * 2048:
		return 2 * 100000000
	elif height > 2048 * 2048 and height <= 8 * 2048 * 2048:
		return 1 * 100000000
	else:
		return 0.5 * 100000000
