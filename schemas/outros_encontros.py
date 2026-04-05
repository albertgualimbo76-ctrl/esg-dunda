from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List, Optional


# 🔹 Base
class OutroEncontroBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    data_hora: datetime
    local: Optional[str] = None  # 📍 Novo campo

    nomes: List[str]
    contactos: List[str]

    # 🔥 Validação: listas devem ter mesmo tamanho
    @field_validator("contactos")
    def validar_listas(cls, contactos, values):
        nomes = values.data.get("nomes")
        if nomes and len(nomes) != len(contactos):
            raise ValueError("nomes e contactos devem ter o mesmo tamanho")
        return contactos


# 🔹 Criar
class OutroEncontroCreate(OutroEncontroBase):
    pass


# 🔹 Atualizar (campos opcionais)
class OutroEncontroUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    data_hora: Optional[datetime] = None
    local: Optional[str] = None  # 📍 Novo campo

    nomes: Optional[List[str]] = None
    contactos: Optional[List[str]] = None

    @field_validator("contactos")
    def validar_listas_update(cls, contactos, values):
        nomes = values.data.get("nomes")
        # só valida se ambos forem enviados
        if nomes is not None and contactos is not None:
            if len(nomes) != len(contactos):
                raise ValueError("nomes e contactos devem ter o mesmo tamanho")
        return contactos


# 🔹 Resposta
class OutroEncontro(OutroEncontroBase):
    id: int
    status: str
    data_alerta: Optional[datetime]
    data_convocatoria: Optional[datetime]
    alerta_enviado: str
    convocatoria_enviada: str
    criado_em: datetime

    class Config:
        from_attributes = True  # ✅ Pydantic v2