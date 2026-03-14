# routers/funcionario_secretaria.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.funcionario_secretaria import FuncionarioSecretaria as FuncionarioSecretariaModel
from schemas.funcionario_secretaria import FuncionarioSecretariaCreate, FuncionarioSecretariaResponse
from utils.normalizar import normalizar_username

router = APIRouter(
    prefix="/funcionarios-secretaria",
    tags=["Funcionário da Secretaria"]
)


# =========================
# CRIAR
# =========================
@router.post("/", response_model=FuncionarioSecretariaResponse)
async def create_funcionario_secretaria(
    funcionario: FuncionarioSecretariaCreate,
    db: AsyncSession = Depends(get_db)
):
    # Normaliza nome
    nome_normalizado = normalizar_username(funcionario.nome)

    # Verifica se já existe
    result = await db.execute(
        select(FuncionarioSecretariaModel).where(FuncionarioSecretariaModel.nome == nome_normalizado)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Funcionário da secretaria já existe")

    db_funcionario = FuncionarioSecretariaModel(
        nome=nome_normalizado,
        senha=funcionario.senha
    )
    db.add(db_funcionario)
    await db.commit()
    await db.refresh(db_funcionario)
    return db_funcionario


# =========================
# LISTAR TODOS
# =========================
@router.get("/", response_model=List[FuncionarioSecretariaResponse])
async def get_funcionarios_secretaria(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FuncionarioSecretariaModel))
    return result.scalars().all()


# =========================
# BUSCAR POR ID
# =========================
@router.get("/{funcionario_id}", response_model=FuncionarioSecretariaResponse)
async def get_funcionario_secretaria(
    funcionario_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(FuncionarioSecretariaModel).where(FuncionarioSecretariaModel.id == funcionario_id)
    )
    funcionario = result.scalar_one_or_none()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário da secretaria não encontrado")
    return funcionario


# =========================
# ATUALIZAR
# =========================
@router.put("/{funcionario_id}", response_model=FuncionarioSecretariaResponse)
async def update_funcionario_secretaria(
    funcionario_id: int,
    funcionario_update: FuncionarioSecretariaCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(FuncionarioSecretariaModel).where(FuncionarioSecretariaModel.id == funcionario_id)
    )
    funcionario = result.scalar_one_or_none()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário da secretaria não encontrado")

    funcionario.nome = normalizar_username(funcionario_update.nome)
    funcionario.senha = funcionario_update.senha

    await db.commit()
    await db.refresh(funcionario)
    return funcionario


# =========================
# APAGAR
# =========================
@router.delete("/{funcionario_id}", response_model=dict)
async def delete_funcionario_secretaria(
    funcionario_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(FuncionarioSecretariaModel).where(FuncionarioSecretariaModel.id == funcionario_id)
    )
    funcionario = result.scalar_one_or_none()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário da secretaria não encontrado")

    await db.delete(funcionario)
    await db.commit()
    return {"message": "Funcionário da secretaria removido com sucesso"}
