from pydantic import BaseModel

class DirectorCreate(BaseModel):
    nome: str
    senha: str

class DirectorResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True
