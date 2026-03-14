from pydantic import BaseModel

class DAPCreate(BaseModel):
    nome: str
    senha: str

class DAPResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True
