from pydantic import BaseModel

class TurmaBase(BaseModel):
    turma: str
    classe_id: int

class TurmaCreate(TurmaBase):
    pass

class TurmaResponse(TurmaBase):
    id: int

    class Config:
        from_attributes = True
