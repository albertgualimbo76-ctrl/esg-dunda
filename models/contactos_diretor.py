from sqlalchemy import Column, Integer, String
from database import Base

class ContactoDiretor(Base):
    __tablename__ = "contactos_diretor"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    cargo = Column(String, nullable=True)  # Ex: "Director" ou "Adjunto Pedagógico"
