from pydantic import BaseModel

# Entrada (criar / atualizar)
class AdminCreate(BaseModel):
    nome: str
    senha: str

# Saída (resposta)
class AdminResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True
