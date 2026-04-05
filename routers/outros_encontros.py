from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.outros_encontros import OutroEncontro
from schemas.outros_encontros import (
    OutroEncontroCreate,
    OutroEncontroUpdate,
    OutroEncontro as OutroEncontroSchema
)
from typing import List
from datetime import timedelta

router = APIRouter(prefix="/outros_encontros", tags=["Outros Encontros"])


# 🔹 Listar todos
@router.get("/", response_model=List[OutroEncontroSchema])
async def listar_encontros(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OutroEncontro))
    encontros = result.scalars().all()
    return encontros


# 🔹 Criar novo encontro
@router.post("/", response_model=OutroEncontroSchema)
async def criar_encontro(encontro: OutroEncontroCreate, db: AsyncSession = Depends(get_db)):

    # Calcula datas automáticas
    data_alerta = encontro.data_hora - timedelta(days=2)
    data_convocatoria = encontro.data_hora - timedelta(days=1)

    # Prepara o novo encontro, incluindo 'local'
    novo_encontro = OutroEncontro(
        **encontro.dict(),
        data_alerta=data_alerta,
        data_convocatoria=data_convocatoria,
        alerta_enviado="NAO",
        convocatoria_enviada="NAO",
        status="APROVADO"
    )

    db.add(novo_encontro)
    await db.commit()
    await db.refresh(novo_encontro)
    return novo_encontro


# 🔹 Detalhes de um encontro
@router.get("/{encontro_id}", response_model=OutroEncontroSchema)
async def detalhes_encontro(encontro_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OutroEncontro).where(OutroEncontro.id == encontro_id))
    encontro = result.scalar_one_or_none()
    if not encontro:
        raise HTTPException(status_code=404, detail="Encontro não encontrado")
    return encontro


# 🔹 Atualizar encontro
@router.put("/{encontro_id}", response_model=OutroEncontroSchema)
async def atualizar_encontro(encontro_id: int, encontro_data: OutroEncontroUpdate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(OutroEncontro).where(OutroEncontro.id == encontro_id))
    encontro = result.scalar_one_or_none()
    if not encontro:
        raise HTTPException(status_code=404, detail="Encontro não encontrado")

    # Atualiza campos
    dados = encontro_data.dict(exclude_unset=True)
    for key, value in dados.items():
        setattr(encontro, key, value)

    # Se a data do encontro foi alterada, recalcula datas automáticas
    if "data_hora" in dados:
        encontro.data_alerta = dados["data_hora"] - timedelta(days=2)
        encontro.data_convocatoria = dados["data_hora"] - timedelta(days=1)
        # Resetar envio de alerta/convocatoria
        encontro.alerta_enviado = "NAO"
        encontro.convocatoria_enviada = "NAO"

    await db.commit()
    await db.refresh(encontro)
    return encontro


# 🔹 Delete encontro
@router.delete("/{encontro_id}")
async def deletar_encontro(encontro_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OutroEncontro).where(OutroEncontro.id == encontro_id))
    encontro = result.scalar_one_or_none()
    if not encontro:
        raise HTTPException(status_code=404, detail="Encontro não encontrado")

    await db.delete(encontro)
    await db.commit()
    return {"detail": "Encontro deletado com sucesso"}