from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.chefe_secretaria import ChefeSecretaria as ChefeSecretariaModel
from schemas.chefe_secretaria import ChefeSecretariaCreate, ChefeSecretariaResponse
from utils.normalizar import normalizar_username

router = APIRouter(prefix="/chefes-secretaria", tags=["Chefe da Secretaria"])


# =========================
# CRIAR
# =========================
@router.post("/", response_model=ChefeSecretariaResponse)
async def create_chefe_secretaria(
    chefe: ChefeSecretariaCreate,
    db: AsyncSession = Depends(get_db)
):
    nome_normalizado = normalizar_username(chefe.nome)

    result = await db.execute(
        select(ChefeSecretariaModel).where(ChefeSecretariaModel.nome == nome_normalizado)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Chefe da secretaria já existe")

    db_chefe = ChefeSecretariaModel(
        nome=nome_normalizado,
        senha=chefe.senha
    )
    db.add(db_chefe)
    await db.commit()
    await db.refresh(db_chefe)
    return db_chefe


# =========================
# LISTAR
# =========================
@router.get("/", response_model=List[ChefeSecretariaResponse])
async def get_chefes_secretaria(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChefeSecretariaModel))
    return result.scalars().all()


# =========================
# BUSCAR POR ID
# =========================
@router.get("/{chefe_id}", response_model=ChefeSecretariaResponse)
async def get_chefe_secretaria(
    chefe_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChefeSecretariaModel).where(ChefeSecretariaModel.id == chefe_id)
    )
    chefe = result.scalar_one_or_none()
    if not chefe:
        raise HTTPException(status_code=404, detail="Chefe da secretaria não encontrado")
    return chefe


# =========================
# ATUALIZAR
# =========================
@router.put("/{chefe_id}", response_model=ChefeSecretariaResponse)
async def update_chefe_secretaria(
    chefe_id: int,
    chefe_update: ChefeSecretariaCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChefeSecretariaModel).where(ChefeSecretariaModel.id == chefe_id)
    )
    chefe = result.scalar_one_or_none()
    if not chefe:
        raise HTTPException(status_code=404, detail="Chefe da secretaria não encontrado")

    chefe.nome = normalizar_username(chefe_update.nome)
    chefe.senha = chefe_update.senha

    await db.commit()
    await db.refresh(chefe)
    return chefe


# =========================
# APAGAR
# =========================
@router.delete("/{chefe_id}", response_model=dict)
async def delete_chefe_secretaria(
    chefe_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChefeSecretariaModel).where(ChefeSecretariaModel.id == chefe_id)
    )
    chefe = result.scalar_one_or_none()
    if not chefe:
        raise HTTPException(status_code=404, detail="Chefe da secretaria não encontrado")

    await db.delete(chefe)
    await db.commit()
    return {"message": "Chefe da secretaria removido com sucesso"}
