import json
import os
import time 
from .block import Block

# Define a classe Blockchain
class Blockchain:
    difficulty = 2  # Número de zeros à esquerda exigido no hash para considerar um bloco como "minado"

    def __init__(self):
        self.unconfirmed_transactions = []  # Lista de transações pendentes (ainda não mineradas)
        self.chain = []                     # Lista que representa a cadeia de blocos (blockchain)
        self.load_chain()                   # Tenta carregar a blockchain de um arquivo local
        if not self.chain:                  # Se a cadeia estiver vazia (primeira execução)
            self.create_genesis_block()     # Cria o bloco gênesis

    # Cria o primeiro bloco da cadeia, com índice 0 e hash anterior "0"
    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()  # Calcula seu hash
        self.chain.append(genesis_block)                   # Adiciona o bloco gênesis à cadeia
        self.save_chain()                                  # Salva a cadeia em arquivo

    # Adiciona um bloco à cadeia, validando sua prova de trabalho
    def add_block(self, block, proof):
        if not self.is_valid_proof(block, proof):  # Verifica se o hash fornecido é válido
            return False
        block.hash = proof                         # Define o hash do bloco
        self.chain.append(block)                   # Adiciona o bloco à cadeia
        self.save_chain()                          # Salva a cadeia atualizada
        return True

    # Verifica se a prova de trabalho é válida
    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * self.difficulty) and 
                block_hash == block.compute_hash())

    # Executa o algoritmo de prova de trabalho (mineração)
    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    # Salva a blockchain e as transações pendentes em um arquivo JSON
    def save_chain(self):
        data = {
            'chain': [block.__dict__ for block in self.chain],  # Serializa cada bloco
            'pending_tx': self.unconfirmed_transactions          # Transações não confirmadas
        }
        with open('blockchain_data.json', 'w') as f:
            json.dump(data, f, indent=4)

    # Carrega a blockchain de um arquivo JSON, se ele existir
    def load_chain(self):
        if os.path.exists('blockchain_data.json'):
            with open('blockchain_data.json', 'r') as f:
                data = json.load(f)
                self.chain = []
                for block_data in data['chain']:
                    block = Block(
                        index=block_data['index'],
                        transactions=block_data['transactions'],
                        timestamp=block_data['timestamp'],
                        previous_hash=block_data['previous_hash']
                    )
                    block.nonce = block_data['nonce']  # Restaura o nonce
                    block.hash = block_data['hash']    # Restaura o hash
                    self.chain.append(block)
                self.unconfirmed_transactions = data['pending_tx']

    # Adiciona uma nova transação à lista de transações pendentes
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
        self.save_chain()

    # Realiza a mineração das transações pendentes
    def mine(self):
        if not self.unconfirmed_transactions:
            return False  # Se não houver transações, não há o que minerar

        last_block = self.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            timestamp=time.time(),
            previous_hash=last_block.hash
        )
        proof = self.proof_of_work(new_block)  # Executa a mineração
        self.add_block(new_block, proof)       # Adiciona o bloco validado à cadeia
        self.unconfirmed_transactions = []     # Limpa a lista de transações pendentes
        return new_block.index                 # Retorna o índice do novo bloco

    # Propriedade que retorna o último bloco da cadeia
    @property
    def last_block(self):
        return self.chain[-1]
