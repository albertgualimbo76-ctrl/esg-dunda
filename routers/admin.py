from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import re
import unicodedata

from database import get_db
from models.admin import Admin as AdminModel
from schemas.admin import AdminCreate, AdminResponse

router = APIRouter(prefix="/admins", tags=["Admins"])


# =========================
# Função utilitária interna
# =========================
def normalizar_username(nome: str) -> str:
    nome = unicodedata.normalize("NFKD", nome)
    nome = nome.encode("ASCII", "ignore").decode("ASCII")
    nome = nome.lower()
    nome = re.sub(r"[^a-z0-9]", "", nome)
    return nome


# =========================
# CRIAR ADMIN
# =========================
@router.post("/", response_model=AdminResponse)
async def create_admin(admin: AdminCreate, db: AsyncSession = Depends(get_db)):
    username = normalizar_username(admin.nome)

    result = await db.execute(
        select(AdminModel).where(AdminModel.nome == username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Usuário já existe")

    db_admin = AdminModel(
        nome=username,
        senha=admin.senha
    )
    db.add(db_admin)
    await db.commit()
    await db.refresh(db_admin)
    return db_admin


# =========================
# LISTAR ADMINS
# =========================
@router.get("/", response_model=List[AdminResponse])
async def get_admins(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdminModel))
    return result.scalars().all()


# =========================
# BUSCAR ADMIN POR ID
# =========================
@router.get("/{admin_id}", response_model=AdminResponse)
async def get_admin(
    admin_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AdminModel).where(AdminModel.id == admin_id)
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin não encontrado")
    return admin


# =========================
# ATUALIZAR ADMIN
# =========================
@router.put("/{admin_id}", response_model=AdminResponse)
async def update_admin(
    admin_id: int,
    admin_update: AdminCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AdminModel).where(AdminModel.id == admin_id)
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin não encontrado")

    admin.nome = normalizar_username(admin_update.nome)
    admin.senha = admin_update.senha

    await db.commit()
    await db.refresh(admin)
    return admin


# =========================
# APAGAR ADMIN
# =========================
@router.delete("/{admin_id}", response_model=dict)
async def delete_admin(admin_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AdminModel).where(AdminModel.id == admin_id)
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin não encontrado")

    await db.delete(admin)
    await db.commit()
    return {"message": "Admin removido com sucesso"}
