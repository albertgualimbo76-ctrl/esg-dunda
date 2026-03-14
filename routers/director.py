from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.director import Director as DirectorModel
from schemas.director import DirectorCreate, DirectorResponse
from utils.normalizar import normalizar_username

router = APIRouter(prefix="/directores", tags=["Director"])


# =========================
# CRIAR DIRECTOR
# =========================
@router.post("/", response_model=DirectorResponse)
async def create_director(director: DirectorCreate, db: AsyncSession = Depends(get_db)):
    nome_normalizado = normalizar_username(director.nome)

    result = await db.execute(
        select(DirectorModel).where(DirectorModel.nome == nome_normalizado)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Director já existe")

    db_director = DirectorModel(
        nome=nome_normalizado,
        senha=director.senha
    )
    db.add(db_director)
    await db.commit()
    await db.refresh(db_director)
    return db_director


# =========================
# LISTAR DIRECTORES
# =========================
@router.get("/", response_model=List[DirectorResponse])
async def get_directores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DirectorModel))
    return result.scalars().all()


# =========================
# BUSCAR DIRECTOR POR ID
# =========================
@router.get("/{director_id}", response_model=DirectorResponse)
async def get_director(
    director_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DirectorModel).where(DirectorModel.id == director_id)
    )
    director = result.scalar_one_or_none()
    if not director:
        raise HTTPException(status_code=404, detail="Director não encontrado")
    return director


# =========================
# ATUALIZAR DIRECTOR
# =========================
@router.put("/{director_id}", response_model=DirectorResponse)
async def update_director(
    director_id: int,
    director_update: DirectorCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DirectorModel).where(DirectorModel.id == director_id)
    )
    director = result.scalar_one_or_none()
    if not director:
        raise HTTPException(status_code=404, detail="Director não encontrado")

    director.nome = normalizar_username(director_update.nome)
    director.senha = director_update.senha

    await db.commit()
    await db.refresh(director)
    return director


# =========================
# APAGAR DIRECTOR
# =========================
@router.delete("/{director_id}", response_model=dict)
async def delete_director(director_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DirectorModel).where(DirectorModel.id == director_id)
    )
    director = result.scalar_one_or_none()
    if not director:
        raise HTTPException(status_code=404, detail="Director não encontrado")

    await db.delete(director)
    await db.commit()
    return {"message": "Director removido com sucesso"}
