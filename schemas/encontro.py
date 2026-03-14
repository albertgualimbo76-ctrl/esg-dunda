from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


# =========================
# ENUM DE TIPOS DE ENCONTRO
# =========================
TipoEncontro = Literal["PROFESSORES", "FUNCIONARIOS"]


# =========================
# SCHEMA PARA CRIAR ENCONTRO
# =========================
class EncontroCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=200)
    descricao: Optional[str] = None
    data_hora: datetime
    tipo: TipoEncontro

    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Reunião Pedagógica",
                "descricao": "Discussão do plano trimestral",
                "data_hora": "2026-02-25T08:00:00",
                "tipo": "PROFESSORES"
            }
        }


# =========================
# SCHEMA PARA ATUALIZAR STATUS
# =========================
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


# =========================
# ENUM TIPO ENCONTRO
# =========================
class TipoEncontro(str, Enum):
    PROFESSORES = "PROFESSORES"
    FUNCIONARIOS = "FUNCIONARIOS"
    DIRECAO = "DIRECAO"


# =========================
# SCHEMA CRIAR
# =========================
class EncontroCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    data_hora: datetime
    tipo: TipoEncontro


# =========================
# SCHEMA UPDATE COMPLETO
# =========================
class EncontroUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    data_hora: Optional[datetime] = None
    tipo: Optional[TipoEncontro] = None
    status: Optional[Literal["APROVADO", "ADIADO", "CANCELADO"]] = None


# =========================
# UPDATE SOMENTE STATUS
# =========================
class EncontroStatusUpdate(BaseModel):
    status: Literal["APROVADO", "ADIADO", "CANCELADO"]


# =========================
# SCHEMA DE RESPOSTA
# =========================
class EncontroResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    data_hora: datetime
    tipo: TipoEncontro
    status: str
    data_alerta: datetime
    data_convocatoria: datetime
    alerta_enviado: str
    convocatoria_enviada: str
    criado_em: datetime

    class Config:
        from_attributes = True
