from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.professor import Professor as ProfessorModel
from schemas.professor import ProfessorCreate, Professor

router = APIRouter(
    prefix="/professores",
    tags=["Professores"]
)

# Criar professor
@router.post("/", response_model=Professor)
async def create_professor(professor: ProfessorCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProfessorModel).where(ProfessorModel.nuit == professor.nuit))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Nuit já cadastrado")

    db_professor = ProfessorModel(
        nome=professor.nome,
        nuit=professor.nuit,
        contacto=professor.contacto,
        sexo=professor.sexo
    )
    db.add(db_professor)
    await db.commit()
    await db.refresh(db_professor)
    return db_professor

# Listar todos professores
@router.get("/", response_model=List[Professor])
async def get_professores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProfessorModel))
    return result.scalars().all()

# Buscar por id
@router.get("/{professor_id}", response_model=Professor)
async def get_professor(professor_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProfessorModel).where(ProfessorModel.id == professor_id))
    professor = result.scalar_one_or_none()
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")
    return professor

# Atualizar
@router.put("/{professor_id}", response_model=Professor)
async def update_professor(professor_id: int, updated_professor: ProfessorCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProfessorModel).where(ProfessorModel.id == professor_id))
    professor = result.scalar_one_or_none()
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    professor.nome = updated_professor.nome
    professor.nuit = updated_professor.nuit
    professor.contacto = updated_professor.contacto
    professor.sexo = updated_professor.sexo

    db.add(professor)
    await db.commit()
    await db.refresh(professor)
    return professor

# Apagar
@router.delete("/{professor_id}", response_model=dict)
async def delete_professor(professor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProfessorModel).where(ProfessorModel.id == professor_id))
    professor = result.scalar_one_or_none()
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")
    await db.delete(professor)
    await db.commit()
    return {"message": f"Professor {professor_id} removido com sucesso"}
