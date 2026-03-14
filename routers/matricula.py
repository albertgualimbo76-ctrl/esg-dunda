from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.aluno import Aluno as AlunoModel
from models.classe import Classe as ClasseModel
from models.turma import Turma as TurmaModel
from models.matricula import Matricula as MatriculaModel
from schemas.matricula import MatriculaCreate, MatriculaResponse

router = APIRouter(prefix="/matriculas", tags=["Matrículas"])

# -------------------
# CREATE
# -------------------
@router.post("/", response_model=MatriculaResponse)
async def create_matricula(
    matricula: MatriculaCreate,
    db: AsyncSession = Depends(get_db)
):
    # 🚫 impedir matrícula duplicada
    stmt_check = select(MatriculaModel).where(
        MatriculaModel.aluno_id == matricula.aluno_id,
        MatriculaModel.ano_letivo == matricula.ano_letivo
    )
    result = await db.execute(stmt_check)
    if result.scalars().first():  # <--- corrigido para evitar MultipleResultsFound
        raise HTTPException(
            status_code=400,
            detail="Este aluno já possui matrícula para este ano letivo"
        )

    db_matricula = MatriculaModel(
        aluno_id=matricula.aluno_id,
        classe_id=matricula.classe_id,
        turma_id=matricula.turma_id,
        ano_letivo=matricula.ano_letivo,
        status="ATIVO"
    )

    db.add(db_matricula)
    await db.commit()
    await db.refresh(db_matricula)

    stmt = (
        select(
            MatriculaModel.id,
            MatriculaModel.ano_letivo,
            MatriculaModel.status,
            AlunoModel.nome.label("aluno_nome"),
            ClasseModel.classe.label("classe_nome"),
            TurmaModel.turma.label("turma_nome")
        )
        .join(AlunoModel, MatriculaModel.aluno_id == AlunoModel.id)
        .join(ClasseModel, MatriculaModel.classe_id == ClasseModel.id)
        .join(TurmaModel, MatriculaModel.turma_id == TurmaModel.id)
        .where(MatriculaModel.id == db_matricula.id)
    )

    result = await db.execute(stmt)
    return result.first()


# -------------------
# READ ALL
# -------------------
@router.get("/", response_model=List[MatriculaResponse])
async def get_matriculas(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(
            MatriculaModel.id,
            MatriculaModel.ano_letivo,
            MatriculaModel.status,
            AlunoModel.nome.label("aluno_nome"),
            ClasseModel.classe.label("classe_nome"),
            TurmaModel.turma.label("turma_nome")
        )
        .join(AlunoModel, MatriculaModel.aluno_id == AlunoModel.id)
        .join(ClasseModel, MatriculaModel.classe_id == ClasseModel.id)
        .join(TurmaModel, MatriculaModel.turma_id == TurmaModel.id)
    )

    result = await db.execute(stmt)
    return result.all()


# -------------------
# READ ONE
# -------------------
@router.get("/{matricula_id}", response_model=MatriculaResponse)
async def get_matricula(
    matricula_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(
            MatriculaModel.id,
            MatriculaModel.ano_letivo,
            MatriculaModel.status,
            AlunoModel.nome.label("aluno_nome"),
            ClasseModel.classe.label("classe_nome"),
            TurmaModel.turma.label("turma_nome")
        )
        .join(AlunoModel, MatriculaModel.aluno_id == AlunoModel.id)
        .join(ClasseModel, MatriculaModel.classe_id == ClasseModel.id)
        .join(TurmaModel, MatriculaModel.turma_id == TurmaModel.id)
        .where(MatriculaModel.id == matricula_id)
    )

    result = await db.execute(stmt)
    matricula = result.first()

    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")

    return matricula


# -------------------
# UPDATE
# -------------------
@router.put("/{matricula_id}", response_model=MatriculaResponse)
async def update_matricula(
    matricula_id: int,
    matricula_update: MatriculaCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MatriculaModel).where(MatriculaModel.id == matricula_id)
    )
    matricula = result.scalar_one_or_none()

    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")

    # 🚫 impedir mudar para um ano duplicado
    stmt_check = select(MatriculaModel).where(
        MatriculaModel.aluno_id == matricula_update.aluno_id,
        MatriculaModel.ano_letivo == matricula_update.ano_letivo,
        MatriculaModel.id != matricula_id
    )
    result = await db.execute(stmt_check)
    if result.scalars().first():  # <--- corrigido
        raise HTTPException(
            status_code=400,
            detail="Este aluno já possui matrícula para este ano letivo"
        )

    matricula.aluno_id = matricula_update.aluno_id
    matricula.classe_id = matricula_update.classe_id
    matricula.turma_id = matricula_update.turma_id
    matricula.ano_letivo = matricula_update.ano_letivo

    await db.commit()

    stmt = (
        select(
            MatriculaModel.id,
            MatriculaModel.ano_letivo,
            MatriculaModel.status,
            AlunoModel.nome.label("aluno_nome"),
            ClasseModel.classe.label("classe_nome"),
            TurmaModel.turma.label("turma_nome")
        )
        .join(AlunoModel, MatriculaModel.aluno_id == AlunoModel.id)
        .join(ClasseModel, MatriculaModel.classe_id == ClasseModel.id)
        .join(TurmaModel, MatriculaModel.turma_id == TurmaModel.id)
        .where(MatriculaModel.id == matricula_id)
    )

    result = await db.execute(stmt)
    return result.first()


# -------------------
# DELETE
# -------------------
@router.delete("/{matricula_id}", response_model=dict)
async def delete_matricula(
    matricula_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MatriculaModel).where(MatriculaModel.id == matricula_id)
    )
    matricula = result.scalar_one_or_none()

    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")

    await db.delete(matricula)
    await db.commit()

    return {"message": f"Matrícula {matricula_id} removida com sucesso"}
