genesis = {
    'testnet': {
        'hash': '',
        'block': ''
    },
    'mainnet': {
        'hash': '',
        'block': ''
    }
}

delegates = 101

def score (votes):
    score = 1.0
    for v in votes:
        score += v
    score /= len (votes)

def reward (round):
    return 1.0