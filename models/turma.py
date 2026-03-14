from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Turma(Base):
    __tablename__ = "turmas"

    id = Column(Integer, primary_key=True, index=True)
    turma = Column(String(10), nullable=False)
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=False)

    classe = relationship("Classe", backref="turmas")
