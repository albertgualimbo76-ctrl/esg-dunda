from pydantic import BaseModel

class ChefeSecretariaCreate(BaseModel):
    nome: str
    senha: str

class ChefeSecretariaResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True
