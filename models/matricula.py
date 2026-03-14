from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class Matricula(Base):
    __tablename__ = "matriculas"
    __table_args__ = (
        UniqueConstraint("aluno_id", "ano_letivo", name="uq_aluno_ano"),
    )

    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    ano_letivo = Column(Integer, nullable=False)
    status = Column(String, default="ATIVO")

    aluno = relationship("Aluno", back_populates="matriculas")
    classe = relationship("Classe")
    turma = relationship("Turma")
