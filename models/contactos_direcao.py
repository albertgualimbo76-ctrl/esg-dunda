from sqlalchemy import Column, Integer, String
from database import Base

class ContactoDirecao(Base):
    __tablename__ = "contactos_direcao"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
