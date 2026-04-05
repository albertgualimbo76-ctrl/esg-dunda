from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


# =========================
# CREATE
# =========================
class EncontroColetivoCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=200)
    descricao: Optional[str] = None
    data_hora: datetime


# =========================
# UPDATE COMPLETO
# =========================
class EncontroColetivoUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    data_hora: Optional[datetime] = None
    status: Optional[Literal["APROVADO", "ADIADO", "CANCELADO"]] = None


# =========================
# UPDATE STATUS
# =========================
class EncontroColetivoStatusUpdate(BaseModel):
    status: Literal["APROVADO", "ADIADO", "CANCELADO"]


# =========================
# RESPONSE
# =========================
class EncontroColetivoResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    data_hora: datetime
    tipo: str
    status: str
    data_alerta: datetime
    data_convocatoria: datetime
    alerta_enviado: str
    convocatoria_enviada: str
    criado_em: datetime

    class Config:
        from_attributes = True