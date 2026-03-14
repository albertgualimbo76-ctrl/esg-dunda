# schemas/usuario_professor.py
from pydantic import BaseModel

class UsuarioProfessorCreate(BaseModel):
    nome: str
    senha: str

class UsuarioProfessorResponse(BaseModel):
    id: int
    nome: str
    senha: str

    class Config:
        orm_mode = True
