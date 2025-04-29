import hashlib
import json

# Define a classe Block, que representa um bloco na blockchain.
class Block:
    # Construtor da classe Block. Recebe informações básicas para inicializar um bloco.
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index  # Posição do bloco na cadeia.
        self.transactions = transactions  # Lista de transações contidas neste bloco.
        self.timestamp = timestamp  # Data e hora da criação do bloco.
        self.previous_hash = previous_hash  # Hash do bloco anterior da cadeia.
        self.nonce = 0  # Número usado para o processo de mineração (proof of work).
        self.hash = self.compute_hash()  # Hash do bloco atual, calculado com base nos dados acima.

    # Método que calcula o hash do bloco atual.
    def compute_hash(self):
        # Converte os atributos do bloco em uma string JSON ordenada (para garantir consistência).
        block_string = json.dumps(self.__dict__, sort_keys=True)
        # Retorna o hash SHA-256 da string codificada.
        return hashlib.sha256(block_string.encode()).hexdigest()