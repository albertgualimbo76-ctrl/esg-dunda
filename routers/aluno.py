from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.aluno import Aluno as AlunoModel
from schemas.aluno import AlunoCreate, Aluno

router = APIRouter(prefix="/alunos", tags=["Alunos"])


# ==============================
# CRIAR ALUNO (SEM DUPLICAÇÃO)
# ==============================
@router.post("/", response_model=Aluno)
async def create_aluno(aluno: AlunoCreate, db: AsyncSession = Depends(get_db)):

    # 🔎 Verifica se já existe aluno com mesmos dados
    result = await db.execute(
        select(AlunoModel).where(
            AlunoModel.nome == aluno.nome,
            AlunoModel.data_nascimento == aluno.data_nascimento,
            AlunoModel.sexo == aluno.sexo
        )
    )

    existente = result.scalar_one_or_none()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Este aluno já foi cadastrado"
        )

    # ➕ Criar novo aluno
    db_aluno = AlunoModel(
        nome=aluno.nome,
        data_nascimento=aluno.data_nascimento,
        sexo=aluno.sexo
    )

    db.add(db_aluno)
    await db.commit()
    await db.refresh(db_aluno)

    return db_aluno


# ==============================
# LISTAR TODOS OS ALUNOS
# ==============================
@router.get("/", response_model=List[Aluno])
async def get_alunos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlunoModel))
    return result.scalars().all()


# ==============================
# BUSCAR ALUNO POR ID
# ==============================
@router.get("/{aluno_id}", response_model=Aluno)
async def get_aluno(
    aluno_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AlunoModel).where(AlunoModel.id == aluno_id)
    )

    aluno = result.scalar_one_or_none()

    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    return aluno


# ==============================
# ATUALIZAR ALUNO
# ==============================
@router.put("/{aluno_id}", response_model=Aluno)
async def update_aluno(
    aluno_id: int,
    aluno_update: AlunoCreate,
    db: AsyncSession = Depends(get_db)
):

    # 🔎 Busca aluno existente
    result = await db.execute(
        select(AlunoModel).where(AlunoModel.id == aluno_id)
    )

    aluno = result.scalar_one_or_none()

    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # 🔎 Verifica duplicação com OUTRO aluno
    result_dup = await db.execute(
        select(AlunoModel).where(
            AlunoModel.nome == aluno_update.nome,
            AlunoModel.data_nascimento == aluno_update.data_nascimento,
            AlunoModel.sexo == aluno_update.sexo,
            AlunoModel.id != aluno_id
        )
    )

    duplicado = result_dup.scalar_one_or_none()

    if duplicado:
        raise HTTPException(
            status_code=400,
            detail="Já existe outro aluno com estes dados"
        )

    # ✏️ Atualizar dados
    aluno.nome = aluno_update.nome
    aluno.data_nascimento = aluno_update.data_nascimento
    aluno.sexo = aluno_update.sexo

    db.add(aluno)
    await db.commit()
    await db.refresh(aluno)

    return aluno


# ==============================
# APAGAR ALUNO
# ==============================
@router.delete("/{aluno_id}", response_model=dict)
async def delete_aluno(aluno_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(AlunoModel).where(AlunoModel.id == aluno_id)
    )

    aluno = result.scalar_one_or_none()

    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    await db.delete(aluno)
    await db.commit()

    return {"message": f"Aluno {aluno_id} removido com sucesso"}
