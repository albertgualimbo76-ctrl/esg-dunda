from sqlalchemy import Column, Integer, String
from database import Base

class Director(Base):
    __tablename__ = "directores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
