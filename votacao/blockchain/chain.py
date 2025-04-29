import json
import os
import time
import logging
from .block import Block


# Cria um logger para registrar mensagens no sistema de log
logger = logging.getLogger(__name__)

# Define a classe Blockchain, que gerencia a cadeia de blocos
class Blockchain:
    # Define a dificuldade da mineração: número de zeros iniciais exigidos no hash
    difficulty = 2

    def __init__(self):
        logger.info("Inicializando Blockchain...")
        self.unconfirmed_transactions = []  # Lista de transações ainda não incluídas na blockchain
        self.chain = []  # Lista que conterá todos os blocos da blockchain
        self.load_chain()  # Tenta carregar blockchain de um arquivo
        if not self.chain:
            self.create_genesis_block()  # Cria o primeiro bloco (gênesis) se a blockchain estiver vazia
        logger.info(f"Blockchain carregada com {len(self.chain)} blocos")

    def create_genesis_block(self):
        # Cria o primeiro bloco da blockchain, com índice 0 e hash anterior "0"
        logger.debug("Criando bloco genesis")
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        self.save_chain()  # Salva o estado da blockchain no arquivo

    def add_block(self, block, proof):
        # Adiciona um bloco à cadeia se a prova (hash) for válida
        if self.is_valid_proof(block, proof):
            self.chain.append(block)
            logger.info(f"Bloco #{block.index} adicionado | Hash: {block.hash[:10]}...")
            logger.debug(f"Detalhes do bloco: {block.__dict__}")
            self.save_chain()
            return True
        logger.warning(f"Bloco inválido rejeitado: {block.hash[:10]}...")
        return False

    def is_valid_proof(self, block, block_hash):
        # Verifica se o hash fornecido começa com os zeros exigidos e é igual ao hash computado do bloco
        valid = (block_hash.startswith('0' * self.difficulty) and 
                 block_hash == block.compute_hash())
        if not valid:
            logger.warning(f"Proof-of-Work inválido para bloco #{block.index}")
        return valid

    def proof_of_work(self, block):
        # Realiza a mineração: encontra um nonce tal que o hash do bloco tenha os zeros necessários
        logger.debug(f"Iniciando mineração do bloco #{block.index}")
        block.nonce = 0
        computed_hash = block.compute_hash()
        attempts = 0

        # Loop até encontrar um hash válido
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
            attempts += 1
            if attempts % 1000 == 0:
                logger.debug(f"Tentativa {attempts} | Nonce: {block.nonce} | Hash: {computed_hash[:10]}...")
        
        logger.info(f"Bloco #{block.index} minerado após {attempts} tentativas")
        return computed_hash

    def save_chain(self):
        # Salva a blockchain e transações pendentes em um arquivo JSON
        try:
            data = {
                'chain': [block.__dict__ for block in self.chain],  # Converte os blocos em dicionários
                'pending_tx': self.unconfirmed_transactions
            }
            with open('blockchain_data.json', 'w') as f:
                json.dump(data, f, indent=4)
            logger.debug("Blockchain salva no arquivo")
        except Exception as e:
            logger.error(f"Erro ao salvar blockchain: {str(e)}", exc_info=True)

    def load_chain(self):
        # Carrega blockchain e transações pendentes de um arquivo JSON, se ele existir
        try:
            if os.path.exists('blockchain_data.json'):
                with open('blockchain_data.json', 'r') as f:
                    data = json.load(f)
                    self.chain = []
                    for block_data in data['chain']:
                        # Reconstrói o objeto Block a partir do dicionário salvo
                        block = Block(
                            index=block_data['index'],
                            transactions=block_data['transactions'],
                            timestamp=block_data['timestamp'],
                            previous_hash=block_data['previous_hash']
                        )
                        block.nonce = block_data['nonce']
                        block.hash = block_data['hash']
                        self.chain.append(block)
                    self.unconfirmed_transactions = data['pending_tx']
                logger.info(f"Blockchain carregada do arquivo: {len(self.chain)} blocos")
        except Exception as e:
            logger.error(f"Erro ao carregar blockchain: {str(e)}", exc_info=True)

    def add_new_transaction(self, transaction):
        # Adiciona uma nova transação à lista de pendentes e salva o estado da blockchain
        try:
            self.unconfirmed_transactions.append(transaction)
            self.save_chain()
            logger.debug(f"Transação adicionada: {transaction['type']}")
        except Exception as e:
            logger.error(f"Erro ao adicionar transação: {str(e)}", exc_info=True)

    def mine(self):
        # Executa o processo de mineração, criando e adicionando um novo bloco com as transações pendentes
        if not self.unconfirmed_transactions:
            logger.warning("Tentativa de mineração sem transações")
            return False

        last_block = self.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            timestamp=time.time(),
            previous_hash=last_block.hash
        )

        logger.info(f"Iniciando mineração do bloco #{new_block.index} com {len(new_block.transactions)} transações")
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []  # Limpa as transações pendentes após mineração
        return new_block.index

    @property
    def last_block(self):
        # Propriedade que retorna o último bloco da cadeia
        return self.chain[-1] if self.chain else None