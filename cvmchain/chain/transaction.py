# Copyright (c) 2016-2017 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import libnacl.sign


class Transaction:
    raw = {
        'type': None,
        'hash': None,
        'from': None,
        'to': None,
        'signature': None,
        'value': None
    }

    def __getitem__ (self, key):
        return self.raw [key]

    def __setitem__ (self, key, value):
        self.raw [key] = value

    def fromJson (data):
        tx = Transaction ()

        if 'type' in data:
            assert (False, 'Notype')

        if data['type'] == 'standard':
            tx['hash'] = data['hash']
            tx['type'] = data['type']
            tx['signature'] = data['signature']
            tx['to'] = data['to']
            tx['from'] = data['from']
            tx['value'] = data['value']
        elif data['type'] == 'multisig':
            pass
        elif data['type'] == 'vote':
            pass

        if not 'hash' in data:
            tx._calculateHash ()

        return tx
            
    def _calculateHash (self):
        self.raw['hash'] = '0c'

    def sign (self, privkey):
        pass

    def validate (self, db):
        # Validate against db informations (balances, etc)
        if db:
            pass

        return True

    def toJson (self):
        return self.raw



class MultisigTransaction (Transaction):
    pass

class StandardTransaction (Transaction):
    pass

class VoteTransaction (Transaction):
    pass
