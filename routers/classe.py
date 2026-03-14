from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.classe import Classe
from schemas.classe import ClasseCreate, ClasseResponse

router = APIRouter(
    prefix="/classes",
    tags=["Classes"]
)

# Criar classe
@router.post("/", response_model=ClasseResponse)
async def criar_classe(
    classe: ClasseCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Classe).where(Classe.classe == classe.classe)
    )
    existente = result.scalar_one_or_none()

    if existente:
        raise HTTPException(status_code=400, detail="Classe já existe")

    nova_classe = Classe(classe=classe.classe)
    db.add(nova_classe)
    await db.commit()
    await db.refresh(nova_classe)
    return nova_classe


# Listar classes
@router.get("/", response_model=List[ClasseResponse])
async def listar_classes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Classe))
    return result.scalars().all()


# Buscar classe por id
@router.get("/{classe_id}", response_model=ClasseResponse)
async def buscar_classe(classe_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Classe).where(Classe.id == classe_id)
    )
    classe = result.scalar_one_or_none()

    if not classe:
        raise HTTPException(status_code=404, detail="Classe não encontrada")

    return classe


# Atualizar classe
@router.put("/{classe_id}", response_model=ClasseResponse)
async def atualizar_classe(
    classe_id: int,
    dados: ClasseCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Classe).where(Classe.id == classe_id)
    )
    classe = result.scalar_one_or_none()

    if not classe:
        raise HTTPException(status_code=404, detail="Classe não encontrada")

    classe.classe = dados.classe
    await db.commit()
    await db.refresh(classe)
    return classe


# Apagar classe
@router.delete("/{classe_id}")
async def apagar_classe(classe_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Classe).where(Classe.id == classe_id)
    )
    classe = result.scalar_one_or_none()

    if not classe:
        raise HTTPException(status_code=404, detail="Classe não encontrada")

    await db.delete(classe)
    await db.commit()
    return {"message": "Classe removida com sucesso"}
