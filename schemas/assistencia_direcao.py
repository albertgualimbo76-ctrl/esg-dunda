from pydantic import BaseModel
from datetime import datetime

class AssistenciaDirecaoCreate(BaseModel):
    professor_assistido_nome: str
    diretor_assistente_nome: str
    classe: str
    turma: str
    disciplina: str
    numero_sala: str
    localizacao_sala: str
    trimestre: str
    data_hora: datetime


class AssistenciaDirecaoResponse(BaseModel):
    id: int
    professor_assistido_nome: str
    diretor_assistente_nome: str
    classe: str
    turma: str
    disciplina: str
    numero_sala: str
    localizacao_sala: str
    trimestre: str
    status_aprovacao: str
    data_hora: datetime
    criado_em: datetime

    model_config = {"from_attributes": True}