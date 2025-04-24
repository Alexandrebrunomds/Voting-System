import hashlib
import json
import time

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        # Construtor do bloco. Recebe:
        # index: posição do bloco na cadeia.
        # transactions: lista de transações contidas no bloco.
        # timestamp: data e hora da criação do bloco.
        # previous_hash: hash do bloco anterior.
        
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()