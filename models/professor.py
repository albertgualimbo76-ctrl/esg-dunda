from sqlalchemy import Column, Integer, String
from database import Base

class Professor(Base):
    __tablename__ = "professores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    nuit = Column(String, unique=True, index=True)
    contacto = Column(String)
    sexo = Column(String(1))
