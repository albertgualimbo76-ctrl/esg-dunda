from sqlalchemy import Column, Integer, String
from database import Base

class Classe(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    classe = Column(String(50), nullable=False, unique=True)
