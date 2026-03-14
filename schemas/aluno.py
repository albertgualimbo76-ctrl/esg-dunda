from pydantic import BaseModel
from datetime import date

# Schema para criar aluno (entrada do usuário)
class AlunoCreate(BaseModel):
    nome: str
    data_nascimento: date
    sexo: str

# Schema para resposta (tem id)
class Aluno(BaseModel):
    id: int
    nome: str
    data_nascimento: date
    sexo: str

    class Config:
        orm_mode = True  # permite converter de ORM SQLAlchemy
