from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Voter(Base):
    """Modelo para representar um eleitor no sistema"""
    __tablename__ = 'voters'
    
    cpf = Column(String(11), primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    has_voted = Column(Boolean, default=False, nullable=False)
    vote = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<Voter(cpf='{self.cpf[:3]}.***.***-**', name='{self.name}')>"

class Candidate(Base):
    """Modelo para representar um candidato na eleição"""
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    party = Column(String(50), nullable=False)
    votes = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.name}', votes={self.votes})>"