from flask import Flask, render_template, request, redirect, url_for, flash  # Módulos do Flask para lidar com rotas e renderização de páginas
from blockchain.chain import Blockchain  # Importa a classe Blockchain definida no projeto
import hashlib  # Para gerar hashes (usado para CPF e blocos)
import time  # Utilizado para marcações de tempo
import logging  # Para geração de logs
from logging.handlers import RotatingFileHandler  # Para salvar logs com limite de tamanho
from datetime import datetime  # Manipulação de datas
from cryptography.hazmat.primitives import hashes  # Hashes para assinatura digital
from cryptography.hazmat.primitives.asymmetric import padding, rsa  # Algoritmos assimétricos (RSA) e preenchimento para assinaturas


# CONFIGURAÇÃO DO SISTEMA DE LOGS


def setup_logging():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Define o formato do log
    formatter = logging.Formatter(log_format)
    
    # Log rotativo para salvar até 5 arquivos de 1MB
    file_handler = RotatingFileHandler(
        'blockchain.log',
        maxBytes=1024*1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Log também no console (terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Aplica handlers ao logger principal
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)

# Chamada para configurar logs ao iniciar o script
setup_logging()
logger = logging.getLogger(__name__)  # Criação do logger local




# CONFIGURAÇÃO DO FLASK


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Chave usada para sessões seguras

# Filtro de template para formatar timestamps no Jinja2
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M:%S'):
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value).strftime(format)
    return value  # Retorna como está se não for timestamp



# INICIALIZAÇÃO DA BLOCKCHAIN E CRIPTOGRAFIA


blockchain = Blockchain()  # Instancia uma nova blockchain

# Gera um par de chaves RSA para assinatura digital
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# Função para assinar transações com a chave privada
def sign_transaction(data: str) -> bytes:
    return private_key.sign(
        data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


# ROTAS FLASK

# Página inicial
@app.route('/')
def index():
    logger.info("Acesso à página inicial")
    return render_template('index.html')  # Retorna o template da página inicial

# Verificação do CPF antes de permitir o voto
@app.route('/verify', methods=['POST'])
def verify():
    try:
        # Limpa a string do CPF (remove . e -)
        cpf = request.form['cpf'].replace('.', '').replace('-', '')
        logger.debug(f"Verificação iniciada para CPF: {cpf[:3]}***")
        
        # Validação do formato do CPF
        if len(cpf) != 11 or not cpf.isdigit():
            logger.warning("CPF inválido submetido")
            flash('CPF inválido. Deve conter 11 dígitos.', 'error')
            return redirect(url_for('index'))

        # Gera um hash do CPF para anonimato
        cpf_hash = hashlib.sha256(cpf.encode()).hexdigest()
        
        # Verifica se esse CPF já votou
        for block in blockchain.chain:
            for tx in block.transactions:
                if tx.get('cpf_hash') == cpf_hash and tx.get('type') == 'vote':
                    logger.warning(f"Tentativa de voto duplicado: {cpf_hash[:6]}...")
                    flash('Este CPF já votou!', 'error')
                    return redirect(url_for('index'))

        logger.info(f"CPF válido: {cpf_hash[:6]}...")
        voter = {'cpf': cpf, 'name': 'Eleitor'}  # Dados fictícios do eleitor
        return render_template('vote.html', voter=voter)
        
    except Exception as e:
        logger.error(f"Erro na verificação: {str(e)}", exc_info=True)
        flash('Erro no processo de verificação', 'error')
        return redirect(url_for('index'))

# Registro do voto
@app.route('/vote', methods=['POST'])
def vote():
    try:
        logger.info("Iniciando processo de votação")
        cpf = request.form['cpf']
        candidate_id = int(request.form['candidate'])  # ID do candidato selecionado
        cpf_hash = hashlib.sha256(cpf.encode()).hexdigest()

        logger.debug(f"Dados do voto - CPF Hash: {cpf_hash[:6]}..., Candidato: {candidate_id}")
        
        # Cria a transação de voto
        transaction = {
            'type': 'vote',
            'cpf_hash': cpf_hash,
            'candidate_id': candidate_id,
            'timestamp': time.time()
        }

        # Assina digitalmente a transação
        transaction['signature'] = sign_transaction(str(transaction)).hex()
        logger.debug("Transação assinada com sucesso")

        # Adiciona a transação à blockchain
        blockchain.add_new_transaction(transaction)
        logger.info("Transação adicionada à pool não confirmada")

        # Minera um novo bloco
        start_time = time.time()
        block_index = blockchain.mine()
        mining_time = time.time() - start_time

        logger.info(f"Bloco #{block_index} minerado em {mining_time:.2f}s")
        flash('Voto registrado na blockchain!', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        logger.error(f"Erro no processo de votação: {str(e)}", exc_info=True)
        flash('Erro ao registrar voto', 'error')
        return redirect(url_for('index'))

# Exibição dos resultados da votação
@app.route('/results')
def results():
    try:
        logger.info("Gerando resultados")
        votes = {}  # Armazena contagem de votos
        candidates = {
            1: {'name': 'Marcela', 'party': 'Chapa 1'},
            2: {'name': 'Fábio', 'party': 'Chapa 2'},
            3: {'name': 'Oswaldo', 'party': 'Chapa 3'}
        }

        # Conta votos por candidato
        for block in blockchain.chain:
            for tx in block.transactions:
                if tx.get('type') == 'vote':
                    candidate_id = tx['candidate_id']
                    votes[candidate_id] = votes.get(candidate_id, 0) + 1

        # Prepara os dados para exibição
        results = []
        for candidate_id, data in candidates.items():
            results.append({
                'name': data['name'],
                'party': data['party'],
                'votes': votes.get(candidate_id, 0)
            })

        logger.debug(f"Resultados calculados: {results}")
        return render_template('results.html', candidates=results)

    except Exception as e:
        logger.error(f"Erro ao gerar resultados: {str(e)}", exc_info=True)
        flash('Erro ao obter resultados', 'error')
        return redirect(url_for('index'))

# Exibição da blockchain completa
@app.route('/blocks')
def show_blocks():
    try:
        logger.info("Solicitação de visualização da blockchain")
        blocks_data = []

        # Coleta dados de cada bloco
        for block in blockchain.chain:
            blocks_data.append({
                'index': block.index,
                'transactions': block.transactions,
                'timestamp': block.timestamp,
                'hash': block.hash,
                'previous_hash': block.previous_hash,
                'nonce': block.nonce
            })

        logger.debug(f"Blocos recuperados: {len(blocks_data)}")
        return render_template('blocks.html', blocks=blocks_data)

    except Exception as e:
        logger.error(f"Erro ao recuperar blocos: {str(e)}", exc_info=True)
        flash('Erro ao carregar blockchain', 'error')
        return redirect(url_for('index'))

# Inicializa o servidor Flask
if __name__ == '__main__':
    logger.info("Iniciando servidor Flask")
    app.run(host='0.0.0.0', port=5000, debug=True)
