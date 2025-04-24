from .block import Block
import time

class Blockchain:
    difficulty = 2 # Define a dificuldade da mineração: o hash deve começar com dois zeros ('00').

    def __init__(self):
        # Construtor da Blockchain.
        self.unconfirmed_transactions = [] # Lista de transações ainda não mineradas
        self.chain = []  # A cadeia de blocos.
        self.create_genesis_block()  # Cria o primeiro bloco da cadeia (bloco gênesis).

    def create_genesis_block(self):
        # Cria o bloco gênesis manualmente, pois não há bloco anterior.
        genesis_block = Block(0, [], time.time(), "0") # Índice 0, sem transações, com hash anterior "0".
        genesis_block.hash = genesis_block.compute_hash()  # Calcula o hash.
        self.chain.append(genesis_block)  # Adiciona o bloco gênesis à cadeia.

    def add_block(self, block, proof):
        # Adiciona um bloco à cadeia, se o hash anterior e a prova forem válidos.
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False  # O hash anterior não corresponde.
        if not self.is_valid_proof(block, proof):
            return False  # A prova de trabalho não é válida.
        block.hash = proof  # Define o hash do bloco como a prova de trabalho.
        self.chain.append(block)  # Adiciona o bloco à cadeia
        return True

    def is_valid_proof(self, block, block_hash):
        # Verifica se a prova de trabalho é válida:
        # - Começa com a quantidade de zeros necessária (dificuldade).
        # - O hash é igual ao gerado pelo bloco.
        return (block_hash.startswith('0' * Blockchain.difficulty) and 
                block_hash == block.compute_hash())

    def proof_of_work(self, block):
        # Algoritmo de mineração: encontra um nonce tal que o hash tenha os zeros à esquerda necessários
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index

    @property
    def last_block(self):
        return self.chain[-1]

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current.hash != current.compute_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
            if not self.is_valid_proof(current, current.hash):
                return False
                
        return True