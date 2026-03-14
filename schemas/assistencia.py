from pydantic import BaseModel
from datetime import datetime

class AssistenciaCreate(BaseModel):
    professor_assistido_id: int
    professor_assistente_id: int
    classe: str
    turma: str
    disciplina: str
    numero_sala: str
    localizacao_sala: str
    trimestre: str
    data_hora: datetime

class AssistenciaResponse(BaseModel):
    id: int
    classe: str
    turma: str
    disciplina: str
    numero_sala: str
    localizacao_sala: str
    trimestre: str
    status_aprovacao: str
    data_hora: datetime
    criado_em: datetime
    professor_assistido_nome: str
    professor_assistente_nome: str

    model_config = {"from_attributes": True}