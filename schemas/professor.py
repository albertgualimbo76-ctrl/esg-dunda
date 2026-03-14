from pydantic import BaseModel

class ProfessorBase(BaseModel):
    nome: str
    nuit: str
    contacto: str
    sexo: str  # 'M' ou 'F'

class ProfessorCreate(ProfessorBase):
    pass

class Professor(ProfessorBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2 para ler SQLAlchemy
