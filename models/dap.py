from sqlalchemy import Column, Integer, String
from database import Base

class DAP(Base):
    __tablename__ = "daps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
