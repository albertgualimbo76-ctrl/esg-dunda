from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class EncontroColetivo(Base):
    __tablename__ = "encontros_coletivo"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    data_hora = Column(DateTime, nullable=False)

    # 🔥 FIXO
    tipo = Column(String, default="COLETIVO")
    status = Column(String, default="APROVADO")

    # 🔥 DATAS AUTOMÁTICAS
    data_alerta = Column(DateTime)
    data_convocatoria = Column(DateTime)

    alerta_enviado = Column(String, default="NAO")
    convocatoria_enviada = Column(String, default="NAO")

    criado_em = Column(DateTime(timezone=True), server_default=func.now())