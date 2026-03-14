from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Type

from database import get_db
from schemas.contactos import ContactoCreate, ContactoUpdate, ContactoResponse

from models.contactos_diretor import ContactoDiretor
from models.contactos_direcao import ContactoDirecao
from models.contactos_professores import ContactoProfessor
from models.contactos_funcionarios import ContactoFuncionario

router = APIRouter(prefix="/contactos", tags=["Contactos"])

# ===========================
# MAPA DE TIPOS
# ===========================
tipo_tabela = {
    "diretor": ContactoDiretor,
    "direcao": ContactoDirecao,
    "professores": ContactoProfessor,
    "funcionarios": ContactoFuncionario
}

# ===========================
# LISTAR CONTACTOS
# ===========================
@router.get("/{tipo}", response_model=List[ContactoResponse])
async def listar_contactos(tipo: str, db: AsyncSession = Depends(get_db)):
    if tipo not in tipo_tabela:
        raise HTTPException(404, "Tipo inválido")
    Model = tipo_tabela[tipo]
    result = await db.execute(select(Model))
    contactos = result.scalars().all()
    return contactos

# ===========================
# CRIAR CONTACTO
# ===========================
@router.post("/{tipo}", response_model=ContactoResponse)
async def criar_contacto(tipo: str, dados: ContactoCreate, db: AsyncSession = Depends(get_db)):
    if tipo not in tipo_tabela:
        raise HTTPException(404, "Tipo inválido")
    Model = tipo_tabela[tipo]
    novo = Model(**dados.dict())
    db.add(novo)
    await db.commit()
    await db.refresh(novo)
    return novo

# ===========================
# ATUALIZAR CONTACTO
# ===========================
@router.put("/{tipo}/{id}", response_model=ContactoResponse)
async def atualizar_contacto(tipo: str, id: int, dados: ContactoUpdate, db: AsyncSession = Depends(get_db)):
    if tipo not in tipo_tabela:
        raise HTTPException(404, "Tipo inválido")
    Model = tipo_tabela[tipo]
    result = await db.execute(select(Model).where(Model.id == id))
    contacto = result.scalar_one_or_none()
    if not contacto:
        raise HTTPException(404, "Contacto não encontrado")

    for key, value in dados.dict(exclude_unset=True).items():
        setattr(contacto, key, value)

    await db.commit()
    await db.refresh(contacto)
    return contacto

# ===========================
# DELETAR CONTACTO
# ===========================
@router.delete("/{tipo}/{id}")
async def deletar_contacto(tipo: str, id: int, db: AsyncSession = Depends(get_db)):
    if tipo not in tipo_tabela:
        raise HTTPException(404, "Tipo inválido")
    Model = tipo_tabela[tipo]
    result = await db.execute(select(Model).where(Model.id == id))
    contacto = result.scalar_one_or_none()
    if not contacto:
        raise HTTPException(404, "Contacto não encontrado")

    await db.delete(contacto)
    await db.commit()
    return {"msg": "Contacto deletado com sucesso"}
