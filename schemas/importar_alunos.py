from pydantic import BaseModel
from datetime import date


class AlunoCreate(BaseModel):
    nome: str
    data_nascimento: date
    sexo: str


class Aluno(BaseModel):
    id: int
    nome: str
    data_nascimento: date
    sexo: str

    class Config:
        orm_mode = True
