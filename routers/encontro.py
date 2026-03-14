# routers/encontro.py
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.encontro import Encontro
from schemas.encontro import EncontroCreate, EncontroResponse, EncontroStatusUpdate

router = APIRouter(prefix="/encontros", tags=["Encontros"])

# ==========================
# CRIAR ENCONTRO
# ==========================
@router.post("/", response_model=EncontroResponse)
async def criar_encontro(dados: EncontroCreate, db: AsyncSession = Depends(get_db)):
    data_alerta = dados.data_hora - timedelta(days=2)
    data_convocatoria = dados.data_hora - timedelta(days=1)

    novo = Encontro(
        titulo=dados.titulo,
        descricao=dados.descricao,
        data_hora=dados.data_hora,
        tipo=dados.tipo,
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
# LISTAR TODOS OS ENCONTROS
# ==========================
@router.get("/", response_model=List[EncontroResponse])
async def listar_encontros(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Encontro))
    encontros = result.scalars().all()
    return encontros

# ==========================
# BUSCAR ENCONTRO POR ID
# ==========================
@router.get("/{encontro_id}", response_model=EncontroResponse)
async def buscar_encontro(encontro_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Encontro).where(Encontro.id == encontro_id))
    encontro = result.scalar_one_or_none()
    if not encontro:
        raise HTTPException(status_code=404, detail="Encontro não encontrado")
    return encontro

# ==========================
# ATUALIZAR ENCONTRO COMPLETO
# ==========================
@router.put("/{encontro_id}", response_model=EncontroResponse)
async def atualizar_encontro(
    encontro_id: int,
    dados: EncontroCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Encontro).where(Encontro.id == encontro_id))
    encontro = result.scalar_one_or_none()
    if not encontro:
        raise HTTPException(status_code=404, detail="Encontro não encontrado")

    encontro.titulo = dados.titulo
    encontro.descricao = dados.descricao
    encontro.data_hora = dados.data_hora
    encontro.tipo = dados.tipo

    # Recalcula datas automáticas
    encontro.data_alerta = dados.data_hora - timedelta(days=2)
    encontro.data_convocatoria = dados.data_hora - timedelta(days=1)

    # Reset alertas enviados
    encontro.alerta_enviado = "NAO"
    encontro.convocatoria_enviada = "NAO"

    await db.commit()
    await db.refresh(encontro)

    return encontro

# ==========================
# ATUALIZAR STATUS
# ==========================
@router.patch("/{encontro_id}/status", response_model=EncontroResponse)
async def atualizar_status_encontro(
    encontro_id: int,
    dados: EncontroStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Encontro).where(Encontro.id == encontro_id))
    encontro = result.scalar_one_or_none()
    if not encontro:
        raise HTTPException(status_code=404, detail="Encontro não encontrado")

    encontro.status = dados.status

    # Se voltar para APROVADO, resetar envios
    if dados.status == "APROVADO":
        encontro.alerta_enviado = "NAO"
        encontro.convocatoria_enviada = "NAO"

    await db.commit()
    await db.refresh(encontro)
    return encontro

# ==========================
# DELETAR ENCONTRO
# ==========================
@router.delete("/{encontro_id}")
async def apagar_encontro(encontro_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Encontro).where(Encontro.id == encontro_id))
    encontro = result.scalar_one_or_none()
    if not encontro:
        raise HTTPException(status_code=404, detail="Encontro não encontrado")

    await db.delete(encontro)
    await db.commit()
    return {"msg": "Encontro apagado com sucesso"}
