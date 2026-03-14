from pydantic import BaseModel, Field
from typing import Optional

# ===========================
# SCHEMA BASE
# ===========================
class ContactoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    telefone: str = Field(..., min_length=9, max_length=15)

# ===========================
# SCHEMA CREATE
# ===========================
class ContactoCreate(ContactoBase):
    pass

# ===========================
# SCHEMA UPDATE
# ===========================
class ContactoUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None

# ===========================
# SCHEMA RESPONSE
# ===========================
class ContactoResponse(ContactoBase):
    id: int

    class Config:
        from_attributes = True
