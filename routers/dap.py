from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.dap import DAP as DAPModel
from schemas.dap import DAPCreate, DAPResponse
from utils.normalizar import normalizar_username

router = APIRouter(prefix="/daps", tags=["DAP"])


# =========================
# CRIAR DAP
# =========================
@router.post("/", response_model=DAPResponse)
async def create_dap(dap: DAPCreate, db: AsyncSession = Depends(get_db)):
    nome_normalizado = normalizar_username(dap.nome)

    result = await db.execute(
        select(DAPModel).where(DAPModel.nome == nome_normalizado)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="DAP já existe")

    db_dap = DAPModel(
        nome=nome_normalizado,
        senha=dap.senha
    )
    db.add(db_dap)
    await db.commit()
    await db.refresh(db_dap)
    return db_dap


# =========================
# LISTAR DAPS
# =========================
@router.get("/", response_model=List[DAPResponse])
async def get_daps(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DAPModel))
    return result.scalars().all()


# =========================
# BUSCAR DAP POR ID
# =========================
@router.get("/{dap_id}", response_model=DAPResponse)
async def get_dap(
    dap_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DAPModel).where(DAPModel.id == dap_id)
    )
    dap = result.scalar_one_or_none()
    if not dap:
        raise HTTPException(status_code=404, detail="DAP não encontrado")
    return dap


# =========================
# ATUALIZAR DAP
# =========================
@router.put("/{dap_id}", response_model=DAPResponse)
async def update_dap(
    dap_id: int,
    dap_update: DAPCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DAPModel).where(DAPModel.id == dap_id)
    )
    dap = result.scalar_one_or_none()
    if not dap:
        raise HTTPException(status_code=404, detail="DAP não encontrado")

    dap.nome = normalizar_username(dap_update.nome)
    dap.senha = dap_update.senha

    await db.commit()
    await db.refresh(dap)
    return dap


# =========================
# APAGAR DAP
# =========================
@router.delete("/{dap_id}", response_model=dict)
async def delete_dap(dap_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DAPModel).where(DAPModel.id == dap_id)
    )
    dap = result.scalar_one_or_none()
    if not dap:
        raise HTTPException(status_code=404, detail="DAP não encontrado")

    await db.delete(dap)
    await db.commit()
    return {"message": "DAP removido com sucesso"}
