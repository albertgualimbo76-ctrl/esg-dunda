# routers/usuario_professor.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.usuario_professor import UsuarioProfessor as UsuarioProfessorModel
from schemas.usuario_professor import UsuarioProfessorCreate, UsuarioProfessorResponse
from utils.normalizar import normalizar_username

router = APIRouter(prefix="/usuarios-professores", tags=["Usuários Professores"])


# =========================
# CRIAR USUÁRIO PROFESSOR
# =========================
@router.post("/", response_model=UsuarioProfessorResponse)
async def create_usuario_professor(usuario: UsuarioProfessorCreate, db: AsyncSession = Depends(get_db)):
    nome_normalizado = normalizar_username(usuario.nome)

    result = await db.execute(
        select(UsuarioProfessorModel).where(UsuarioProfessorModel.nome == nome_normalizado)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Usuário professor já existe")

    db_usuario = UsuarioProfessorModel(nome=nome_normalizado, senha=usuario.senha)
    db.add(db_usuario)
    await db.commit()
    await db.refresh(db_usuario)
    return db_usuario


# =========================
# LISTAR TODOS
# =========================
@router.get("/", response_model=List[UsuarioProfessorResponse])
async def get_usuarios_professores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UsuarioProfessorModel))
    return result.scalars().all()


# =========================
# BUSCAR POR ID
# =========================
@router.get("/{usuario_id}", response_model=UsuarioProfessorResponse)
async def get_usuario_professor(usuario_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UsuarioProfessorModel).where(UsuarioProfessorModel.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário professor não encontrado")
    return usuario


# =========================
# ATUALIZAR
# =========================
@router.put("/{usuario_id}", response_model=UsuarioProfessorResponse)
async def update_usuario_professor(usuario_id: int, usuario_update: UsuarioProfessorCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UsuarioProfessorModel).where(UsuarioProfessorModel.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário professor não encontrado")

    usuario.nome = normalizar_username(usuario_update.nome)
    usuario.senha = usuario_update.senha

    await db.commit()
    await db.refresh(usuario)
    return usuario


# =========================
# APAGAR
# =========================
@router.delete("/{usuario_id}", response_model=dict)
async def delete_usuario_professor(usuario_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UsuarioProfessorModel).where(UsuarioProfessorModel.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário professor não encontrado")

    await db.delete(usuario)
    await db.commit()
    return {"message": "Usuário professor removido com sucesso"}
