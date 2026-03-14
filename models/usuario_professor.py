# models/usuario_professor.py
from sqlalchemy import Column, Integer, String
from database import Base

class UsuarioProfessor(Base):
    __tablename__ = "usuarios_professores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
