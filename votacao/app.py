from flask import Flask, render_template, request, redirect, url_for, flash
from blockchain.chain import Blockchain
from database.operations import (
    register_voter,
    verify_voter,
    record_vote,
    get_results,
    init_database
)
from database.models import Voter, Candidate
import hashlib
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_complexa_aqui'

# Inicialização do sistema
blockchain = Blockchain()
init_database()

# Configuração de criptografia
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

def sign_transaction(data: str) -> bytes:
    """Assina digitalmente uma transação"""
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
    """Página inicial com formulário de CPF"""
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    """Verifica o eleitor e redireciona para votação"""
    try:
        cpf = request.form['cpf'].replace('.', '').replace('-', '')
        
        if len(cpf) != 11 or not cpf.isdigit():
            flash('CPF inválido. Deve conter 11 dígitos.', 'error')
            return redirect(url_for('index'))
            
        voter = verify_voter(cpf)
        
        if not voter:
            flash('CPF não cadastrado no sistema.', 'error')
            return redirect(url_for('register', cpf=cpf))
        
        if voter.has_voted:
            flash('Este CPF já votou.', 'error')
            return redirect(url_for('index'))
        
        return render_template('vote.html', voter=voter)
        
    except Exception as e:
        flash(f'Erro ao verificar eleitor: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Cadastra novos eleitores"""
    if request.method == 'POST':
        try:
            cpf = request.form['cpf'].replace('.', '').replace('-', '')
            name = request.form['name'].strip()
            
            if len(cpf) != 11 or not cpf.isdigit():
                flash('CPF inválido. Deve conter 11 dígitos.', 'error')
                return redirect(url_for('register'))
                
            if register_voter(cpf, name):
                flash('Eleitor cadastrado com sucesso!', 'success')
                return redirect(url_for('verify'), code=307)  # Redireciona mantendo POST
            else:
                flash('CPF já cadastrado no sistema.', 'error')
                
        except Exception as e:
            flash(f'Erro no cadastro: {str(e)}', 'error')
        
        return redirect(url_for('register'))
    
    # GET: Mostra formulário com CPF pré-preenchido se fornecido
    cpf = request.args.get('cpf', '')
    return render_template('register.html', cpf=cpf)

@app.route('/vote', methods=['POST'])
def vote():
    """Processa o voto do eleitor"""
    try:
        cpf = request.form['cpf']
        candidate_id = int(request.form['candidate'])
        
        if record_vote(cpf, candidate_id):
            # Registra na blockchain
            transaction = {
                'hashed_cpf': hashlib.sha256(cpf.encode()).hexdigest(),
                'candidate_id': candidate_id,
                'timestamp': time.time()
            }
            transaction['signature'] = sign_transaction(str(transaction)).hex()
            blockchain.add_new_transaction(transaction)
            blockchain.mine()
            
            flash('Voto registrado com sucesso!', 'success')
        else:
            flash('Erro ao registrar voto. Eleitor já votou ou dados inválidos.', 'error')
            
    except Exception as e:
        flash(f'Erro no processo de votação: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/results')
def results():
    """Exibe os resultados da votação"""
    try:
        candidates = get_results()
        return render_template('results.html', candidates=candidates)
    except Exception as e:
        flash(f'Erro ao obter resultados: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)