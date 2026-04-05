from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base

class OutroEncontro(Base):
    __tablename__ = "outros_encontros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    data_hora = Column(DateTime, nullable=False)

    # 🔥 LISTAS (JSON)
    nomes = Column(JSON, nullable=False)        # ["João", "Maria"]
    contactos = Column(JSON, nullable=False)    # ["841234567", "821234567"]

    status = Column(String, default="APROVADO")

    # 🔥 DATAS AUTOMÁTICAS (mantidas)
    data_alerta = Column(DateTime)
    data_convocatoria = Column(DateTime)

    alerta_enviado = Column(String, default="NAO")
    convocatoria_enviada = Column(String, default="NAO")

    # 📍 Local do encontro
    local = Column(String(255), nullable=True)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())