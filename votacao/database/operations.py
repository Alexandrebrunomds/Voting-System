from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Voter, Candidate
import os

# Configuração do banco de dados
DB_DIR = 'database'
DB_NAME = 'voting_system.db'
DB_PATH = os.path.join(DB_DIR, DB_NAME)

# Cria o diretório se não existir
os.makedirs(DB_DIR, exist_ok=True)

engine = create_engine(f'sqlite:///{DB_PATH}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def register_voter(cpf: str, name: str) -> bool:
    """Registra um novo eleitor no sistema"""
    session = Session()
    try:
        if session.query(Voter).filter_by(cpf=cpf).first():
            return False
            
        voter = Voter(cpf=cpf, name=name)
        session.add(voter)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def verify_voter(cpf: str) -> Voter | None:
    """Verifica se um eleitor está cadastrado"""
    session = Session()
    try:
        return session.query(Voter).filter_by(cpf=cpf).first()
    finally:
        session.close()

def record_vote(cpf: str, candidate_id: int) -> bool:
    """Registra o voto de um eleitor"""
    session = Session()
    try:
        voter = session.query(Voter).filter_by(cpf=cpf).first()
        candidate = session.query(Candidate).filter_by(id=candidate_id).first()
        
        if not voter or not candidate or voter.has_voted:
            return False
            
        voter.has_voted = True
        voter.vote = candidate_id
        candidate.votes += 1
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_results() -> list[Candidate]:
    """Obtém os resultados ordenados por votos"""
    session = Session()
    try:
        return session.query(Candidate).order_by(Candidate.votes.desc()).all()
    finally:
        session.close()

def init_database():
    """Inicializa o banco com dados de teste"""
    session = Session()
    try:
        # Candidatos padrão
        if not session.query(Candidate).first():
            candidates = [
                Candidate(name="Candidato A", party="Partido X"),
                Candidate(name="Candidato B", party="Partido Y"),
                Candidate(name="Candidato C", party="Partido Z")
            ]
            session.add_all(candidates)
        
        # Eleitores de teste (opcional)
        if not session.query(Voter).first():
            voters = [
                Voter(cpf="12345678901", name="Eleitor Teste 1"),
                Voter(cpf="98765432109", name="Eleitor Teste 2")
            ]
            session.add_all(voters)
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()