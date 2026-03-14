from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.turma import Turma
from models.classe import Classe
from schemas.turma import TurmaCreate, TurmaResponse

router = APIRouter(
    prefix="/turmas",
    tags=["Turmas"]
)

# Criar turma
@router.post("/", response_model=TurmaResponse)
async def criar_turma(
    turma: TurmaCreate,
    db: AsyncSession = Depends(get_db)
):
    # verificar se a classe existe
    result = await db.execute(
        select(Classe).where(Classe.id == turma.classe_id)
    )
    classe = result.scalar_one_or_none()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe não encontrada")

    nova_turma = Turma(
        turma=turma.turma,
        classe_id=turma.classe_id
    )
    db.add(nova_turma)
    await db.commit()
    await db.refresh(nova_turma)
    return nova_turma


# Listar turmas
@router.get("/", response_model=List[TurmaResponse])
async def listar_turmas(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Turma))
    return result.scalars().all()


# Buscar turma por id
@router.get("/{turma_id}", response_model=TurmaResponse)
async def buscar_turma(turma_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Turma).where(Turma.id == turma_id)
    )
    turma = result.scalar_one_or_none()

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    return turma


# Atualizar turma
@router.put("/{turma_id}", response_model=TurmaResponse)
async def atualizar_turma(
    turma_id: int,
    dados: TurmaCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Turma).where(Turma.id == turma_id)
    )
    turma_db = result.scalar_one_or_none()

    if not turma_db:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    turma_db.turma = dados.turma
    turma_db.classe_id = dados.classe_id

    await db.commit()
    await db.refresh(turma_db)
    return turma_db


# Apagar turma
@router.delete("/{turma_id}")
async def apagar_turma(turma_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Turma).where(Turma.id == turma_id)
    )
    turma = result.scalar_one_or_none()

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    await db.delete(turma)
    await db.commit()
    return {"message": "Turma removida com sucesso"}
