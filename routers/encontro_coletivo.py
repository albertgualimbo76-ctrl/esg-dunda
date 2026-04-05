from datetime import timedelta, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.encontro_coletivo import EncontroColetivo
from schemas.encontro_coletivo import (
    EncontroColetivoCreate,
    EncontroColetivoUpdate,
    EncontroColetivoResponse,
    EncontroColetivoStatusUpdate
)

router = APIRouter(prefix="/coletivo", tags=["Coletivo"])


# ==========================
# CRIAR
# ==========================
@router.post("/", response_model=EncontroColetivoResponse)
async def criar_encontro(
    dados: EncontroColetivoCreate,
    db: AsyncSession = Depends(get_db)
):
    data_alerta = dados.data_hora - timedelta(days=2)
    data_convocatoria = dados.data_hora - timedelta(days=1)

    novo = EncontroColetivo(
        titulo=dados.titulo,
        descricao=dados.descricao,
        data_hora=dados.data_hora,
        tipo="COLETIVO",
        status="APROVADO",
        data_alerta=data_alerta,
        data_convocatoria=data_convocatoria,
        alerta_enviado="NAO",
        convocatoria_enviada="NAO"
    )

    db.add(novo)
    await db.commit()
    await db.refresh(novo)

    return novo


# ==========================
# LISTAR TODOS
# ==========================
@router.get("/", response_model=List[EncontroColetivoResponse])
async def listar_encontros(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EncontroColetivo))
    return result.scalars().all()


# ==========================
# BUSCAR POR ID
# ==========================
@router.get("/{encontro_id}", response_model=EncontroColetivoResponse)
async def buscar_encontro(
    encontro_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(EncontroColetivo).where(EncontroColetivo.id == encontro_id)
    )
    encontro = result.scalar_one_or_none()

    if not encontro:
        raise HTTPException(status_code=404, detail="Encontro não encontrado")

    return encontro


# ==========================
# ATUALIZAR COMPLETO
# ==========================
@router.put("/{encontro_id}", response_model=EncontroColetivoResponse)
async def atualizar_encontro(
    encontro_id: int,
    dados: EncontroColetivoUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(EncontroColetivo).where(EncontroColetivo.id == encontro_id)
    )
    encontro = result.scalar_one_or_none()

    if not encontro:
        raise HTTPException(status_code=404, detail="Encontro não encontrado")

    if dados.titulo is not None:
        encontro.titulo = dados.titulo

    if dados.descricao is not None:
        encontro.descricao = dados.descricao

    if dados.data_hora is not None:
        encontro.data_hora = dados.data_hora

        # 🔥 recalcular datas
        encontro.data_alerta = dados.data_hora - timedelta(days=2)
        encontro.data_convocatoria = dados.data_hora - timedelta(days=1)

        # 🔥 reset envio
        encontro.alerta_enviado = "NAO"
        encontro.convocatoria_enviada = "NAO"

    if dados.status is not None:
        encontro.status = dados.status

    await db.commit()
    await db.refresh(encontro)

    return encontro


# ==========================
# ATUALIZAR STATUS
# ==========================
@router.patch("/{encontro_id}/status", response_model=EncontroColetivoResponse)
async def atualizar_status(
    encontro_id: int,
    dados: EncontroColetivoStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(EncontroColetivo).where(EncontroColetivo.id == encontro_id)
    )
    encontro = result.scalar_one_or_none()

    if not encontro:
        raise HTTPException(status_code=404, detail="Encontro não encontrado")

    encontro.status = dados.status

    if dados.status == "APROVADO":
        encontro.alerta_enviado = "NAO"
        encontro.convocatoria_enviada = "NAO"

    await db.commit()
    await db.refresh(encontro)

    return encontro


# ==========================
# DELETAR
# ==========================
@router.delete("/{encontro_id}")
async def deletar_encontro(
    encontro_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(EncontroColetivo).where(EncontroColetivo.id == encontro_id)
    )
    encontro = result.scalar_one_or_none()

    if not encontro:
        raise HTTPException(status_code=404, detail="Encontro não encontrado")

    await db.delete(encontro)
    await db.commit()

    return {"msg": "Encontro do coletivo apagado com sucesso"}


# ==========================
# EXTRA: PRÓXIMOS ENCONTROS
# ==========================
@router.get("/proximos", response_model=List[EncontroColetivoResponse])
async def proximos_encontros(db: AsyncSession = Depends(get_db)):
    agora = datetime.utcnow()

    result = await db.execute(
        select(EncontroColetivo).where(
            EncontroColetivo.data_hora >= agora
        )
    )

    return result.scalars().all()