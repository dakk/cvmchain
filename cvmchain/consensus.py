# Genesis block
genesis = {
	'testnet': {
		"hash": "e0693b363a4595f0d2d4133fb854e308059f1ca9e11e4145e13bc2e0ff2639bf",
		"prev": "0000000000000000000000000000000000000000000000000000000000000000",
		"height": 0,
		"forger": "A5rr5hr1i4FqrjvfnEFybdSmxeULdRQEb1gBgvrihqYD",
		"timestamp": 1482796800,
		"transactions": [],
		"roothash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
		"signature": "4E7bYx2xR1wehkNS0sZKuWlkug7B82S4OVISllCyBrSfcRdycLjXkE4Wv3Jw9GHsT75iY4mKGYBtqqW67kAfAg=="
	},
	'mainnet': {
		"hash": "",
		"height": 0,
		"forger": "",
		"timestamp": 1482796800,
		"transactios": [],
		"signature": ""
	}
}

# Genesis block reward
genesis_reward = 1000 * 100000000

# Number of delegates
delegates = 101

def score (votes):
	score = 1.0
	for v in votes:
		score += v
	score /= len (votes)

def reward (round):
	return 1.0