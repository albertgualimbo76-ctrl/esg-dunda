from sqlalchemy import Column, Integer, String, Date, Sequence
from database import Base


class Aluno(Base):
    __tablename__ = "alunos"   # 👈 grava na tabela existente

    id = Column(
        Integer,
        Sequence('aluno_id_seq', start=10000),
        primary_key=True,
        index=True
    )

    nome = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    sexo = Column(String(1), nullable=False)
