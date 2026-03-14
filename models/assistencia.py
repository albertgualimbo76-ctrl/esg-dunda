from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class AssistenciaMutua(Base):
    __tablename__ = "assistencias_mutuas"

    id = Column(Integer, primary_key=True, index=True)

    # Relacionamento com os professores (não estamos salvando o ID diretamente)
    professor_assistido_nome = Column(String, nullable=False)
    professor_assistente_nome = Column(String, nullable=False)

    classe = Column(String, nullable=False)
    turma = Column(String, nullable=False)
    disciplina = Column(String, nullable=False)

    numero_sala = Column(String, nullable=False)
    localizacao_sala = Column(String, nullable=False)

    trimestre = Column(String, nullable=False)
    status_aprovacao = Column(String, default="NAO")

    data_hora = Column(DateTime, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
