from flask import Flask, render_template, request, redirect, url_for, flash
from blockchain.chain import Blockchain
import hashlib
import time
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Filtro para formatar timestamps
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M:%S'):
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value).strftime(format)
    return value

blockchain = Blockchain()

# Configuração de criptografia
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

def sign_transaction(data: str) -> bytes:
    return private_key.sign(
        data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    try:
        cpf = request.form['cpf'].replace('.', '').replace('-', '')
        if len(cpf) != 11 or not cpf.isdigit():
            flash('CPF inválido. Deve conter 11 dígitos.', 'error')
            return redirect(url_for('index'))
            
        cpf_hash = hashlib.sha256(cpf.encode()).hexdigest()
        
        # Verifica se já votou
        for block in blockchain.chain:
            for tx in block.transactions:
                if tx.get('cpf_hash') == cpf_hash and tx.get('type') == 'vote':
                    flash('Este CPF já votou!', 'error')
                    return redirect(url_for('index'))
        
        voter = {'cpf': cpf, 'name': 'Eleitor'}
        return render_template('vote.html', voter=voter)
        
    except Exception as e:
        flash(f'Erro ao verificar: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/vote', methods=['POST'])
def vote():
    try:
        cpf = request.form['cpf']
        candidate_id = int(request.form['candidate'])
        
        transaction = {
            'type': 'vote',
            'cpf_hash': hashlib.sha256(cpf.encode()).hexdigest(),
            'candidate_id': candidate_id,
            'timestamp': time.time()
        }
        
        transaction['signature'] = sign_transaction(str(transaction)).hex()
        blockchain.add_new_transaction(transaction)
        blockchain.mine()
        flash('Voto registrado na blockchain!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Erro ao votar: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    try:
        votes = {}
        candidates = {
            1: {'name': 'Marcela', 'party': 'Chapa 1'},
            2: {'name': 'Fábio', 'party': 'Chapa 2'},
            3: {'name': 'Oswaldo', 'party': 'Chapa 3'}
        }
        
        for block in blockchain.chain:
            for tx in block.transactions:
                if tx.get('type') == 'vote':
                    candidate_id = tx['candidate_id']
                    votes[candidate_id] = votes.get(candidate_id, 0) + 1
        
        results = []
        for candidate_id, data in candidates.items():
            results.append({
                'name': data['name'],
                'party': data['party'],
                'votes': votes.get(candidate_id, 0)
            })
        
        return render_template('results.html', candidates=results)
    except Exception as e:
        flash(f'Erro ao calcular resultados: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/blocks')
def show_blocks():
    try:
        blocks_data = []
        for block in blockchain.chain:
            blocks_data.append({
                'index': block.index,
                'transactions': block.transactions,
                'timestamp': block.timestamp,
                'hash': block.hash,
                'previous_hash': block.previous_hash,
                'nonce': block.nonce
            })
        return render_template('blocks.html', blocks=blocks_data)
    except Exception as e:
        flash(f'Erro ao carregar blocos: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)