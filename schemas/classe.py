from pydantic import BaseModel

class ClasseBase(BaseModel):
    classe: str

class ClasseCreate(ClasseBase):
    pass

class ClasseResponse(ClasseBase):
    id: int

    class Config:
        from_attributes = True
