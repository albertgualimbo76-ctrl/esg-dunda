from pydantic import BaseModel

class MatriculaCreate(BaseModel):
    aluno_id: int
    classe_id: int
    turma_id: int
    ano_letivo: int


class MatriculaResponse(BaseModel):
    id: int
    ano_letivo: int
    status: str
    aluno_nome: str
    classe_nome: str
    turma_nome: str

    class Config:
        from_attributes = True
