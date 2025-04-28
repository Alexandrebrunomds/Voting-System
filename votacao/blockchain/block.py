import hashlib 
import json

# Define a classe Block, que representa um bloco na blockchain
class Block:
    # Construtor da classe. Inicializa os atributos do bloco.
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index                      # Índice do bloco na cadeia
        self.transactions = transactions        # Lista de transações contidas no bloco
        self.timestamp = timestamp              # Carimbo de data/hora em que o bloco foi criado
        self.previous_hash = previous_hash      # Hash do bloco anterior na cadeia
        self.nonce = 0                          # Valor que será ajustado durante a mineração (proof of work)
        self.hash = self.compute_hash()         # Hash do próprio bloco, calculado com base em seus dados

    # Método para calcular o hash do bloco atual
    def compute_hash(self):
        # Converte o dicionário de atributos do bloco em uma string JSON ordenada
        block_string = json.dumps(self.__dict__, sort_keys=True)
        # Codifica a string em bytes e retorna o hash SHA-256 como uma string hexadecimal
        return hashlib.sha256(block_string.encode()).hexdigest()
