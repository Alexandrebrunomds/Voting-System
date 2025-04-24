from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() # Cria uma base para as classes que representam tabelas no banco.

class Voter(Base):
    __tablename__ = 'voters' # Nome da tabela no banco.
    
    cpf = Column(String(11), primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    has_voted = Column(Boolean, default=False, nullable=False)
    vote = Column(String(50), nullable=True)

    def __repr__(self):
        # Representação legível do objeto (oculta parte do CPF).
        return f"<Voter(cpf='{self.cpf[:3]}.***.***-**', name='{self.name}')>"

class Candidate(Base):
    __tablename__ = 'candidates' # Nome da tabela no banco.
    
    id = Column(Integer, primary_key=True, autoincrement=True) # ID autoincrementável.
    name = Column(String(100), nullable=False) # Nome do candidato.
    party = Column(String(50), nullable=False) # Partido ou chapa.
    votes = Column(Integer, default=0, nullable=False) # Contador de votos recebidos.

    def __repr__(self):
        # Representação legível do objeto candidato.
        return f"<Candidate(id={self.id}, name='{self.name}', votes={self.votes})>"