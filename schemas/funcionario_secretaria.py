from pydantic import BaseModel

class FuncionarioSecretariaCreate(BaseModel):
    nome: str
    senha: str

class FuncionarioSecretariaResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True
