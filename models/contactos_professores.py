from sqlalchemy import Column, Integer, String
from database import Base

class ContactoProfessor(Base):
    __tablename__ = "contactos_professores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
