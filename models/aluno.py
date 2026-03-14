from sqlalchemy import Column, Integer, String, Date, Sequence
from sqlalchemy.orm import relationship
from database import Base

class Aluno(Base):
    __tablename__ = "alunos"

    id = Column(
        Integer,
        Sequence('aluno_id_seq', start=10000),  # começa em 10000
        primary_key=True,
        index=True
    )

    nome = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    sexo = Column(String(1), nullable=False)

    matriculas = relationship(
        "Matricula",
        back_populates="aluno",
        cascade="all, delete-orphan"
    )

    @property
    def matricula_atual(self):
        if self.matriculas:
            return sorted(self.matriculas, key=lambda m: m.id)[-1]
        return None
