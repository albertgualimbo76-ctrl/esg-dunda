from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.aluno import Aluno as AlunoModel
import pandas as pd
from io import BytesIO
from datetime import datetime

router = APIRouter(prefix="/importar-alunos", tags=["Importar Alunos"])

@router.post("/", response_model=dict)
async def importar_excel(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    conteudo = await file.read()
    df = pd.read_excel(BytesIO(conteudo))

    adicionados = 0
    ignorados = 0

    for _, row in df.iterrows():
        nome = str(row.get("nome", "")).strip()  # remove espaços extras
        data_raw = row.get("data_nascimento")
        sexo = str(row.get("sexo", "")).strip().upper()

        # Ignora linhas incompletas
        if not nome or not data_raw or sexo not in ("M", "F"):
            continue

        # Converte data para date
        try:
            if isinstance(data_raw, str):
                if "/" in data_raw:  # dd/mm/yyyy
                    data_nascimento = datetime.strptime(data_raw, "%d/%m/%Y").date()
                elif "-" in data_raw:  # yyyy-mm-dd
                    data_nascimento = datetime.strptime(data_raw, "%Y-%m-%d").date()
                else:
                    continue
            elif isinstance(data_raw, (pd.Timestamp, datetime)):
                data_nascimento = data_raw.date()
            else:
                continue
        except:
            continue

        # 🔎 Verifica se existe aluno com mesmo NOME exato, MESMA DATA e SEXO
        result = await db.execute(
            select(AlunoModel).where(
                AlunoModel.nome == nome,
                AlunoModel.data_nascimento == data_nascimento,
                AlunoModel.sexo == sexo
            )
        )
        existente = result.scalar_one_or_none()

        if existente:
            ignorados += 1
            continue

        # ➕ Cria o aluno automaticamente
        db_aluno = AlunoModel(
            nome=nome,
            data_nascimento=data_nascimento,
            sexo=sexo
        )
        db.add(db_aluno)
        adicionados += 1

    await db.commit()

    return {
        "mensagem": "Importação concluída",
        "adicionados": adicionados,
        "ignorados": ignorados
    }
