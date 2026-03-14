from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import List
from database import get_db
from models.assistencia import AssistenciaMutua
from models.contactos_professores import ContactoProfessor  # Apenas essa tabela
from schemas.assistencia import AssistenciaCreate, AssistenciaResponse

router = APIRouter(prefix="/assistencias", tags=["Assistências Mútuas"])

# -----------------------------
# Listar professores (dropdown)
# -----------------------------
@router.get("/professores")
async def listar_professores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContactoProfessor))
    professores = result.scalars().all()
    return [{"id": p.id, "nome": p.nome} for p in professores]

# -----------------------------
# Criar assistência
# -----------------------------
@router.post("/", response_model=AssistenciaResponse)
async def criar_assistencia(dados: AssistenciaCreate, db: AsyncSession = Depends(get_db)):
    # Buscar o professor assistido na tabela ContactoProfessor
    assistido = await db.get(ContactoProfessor, dados.professor_assistido_id)
    # Buscar o professor assistente na tabela ContactoProfessor
    assistente = await db.get(ContactoProfessor, dados.professor_assistente_id)

    # Verificar se ambos os registros foram encontrados
    if not assistido:
        raise HTTPException(status_code=404, detail="Professor assistido não encontrado")
    if not assistente:
        raise HTTPException(status_code=404, detail="Professor assistente não encontrado")

    # Criar nova assistência
    nova = AssistenciaMutua(
        professor_assistido_nome=assistido.nome,
        professor_assistente_nome=assistente.nome,
        classe=dados.classe,
        turma=dados.turma,
        disciplina=dados.disciplina,
        numero_sala=dados.numero_sala,
        localizacao_sala=dados.localizacao_sala,
        trimestre=dados.trimestre,
        data_hora=dados.data_hora
    )

    # Adicionar no banco de dados
    db.add(nova)
    await db.commit()
    await db.refresh(nova)

    return nova

# -----------------------------
# Listar assistências
# -----------------------------
@router.get("/", response_model=List[AssistenciaResponse])
async def listar_assistencias(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AssistenciaMutua))
    assistencias = result.scalars().all()
    return assistencias

# -----------------------------
# Aprovar/Desaprovar trimestre
# -----------------------------
@router.put("/aprovar-trimestre")
async def alterar_status_trimestre(
        trimestre: int = Query(..., ge=1, le=3),
        status: str = Query(..., regex="^(APROVADO|NAO)$"),
        db: AsyncSession = Depends(get_db)
):
    await db.execute(
        update(AssistenciaMutua)
        .where(AssistenciaMutua.trimestre == str(trimestre))
        .values(status_aprovacao=status)
    )
    await db.commit()
    return {"message": f"Trimestre {trimestre} atualizado para {status}"}

# -----------------------------
# Obter assistência por ID
# -----------------------------
@router.get("/id/{id}", response_model=AssistenciaResponse)
async def obter_assistencia(id: int, db: AsyncSession = Depends(get_db)):
    assistencia = await db.get(AssistenciaMutua, id)
    if not assistencia:
        raise HTTPException(status_code=404, detail="Assistência não encontrada")
    return assistencia

# -----------------------------
# Atualizar assistência por ID
# -----------------------------
@router.put("/id/{id}", response_model=AssistenciaResponse)
async def atualizar_assistencia(id: int, dados: AssistenciaCreate, db: AsyncSession = Depends(get_db)):
    assistencia = await db.get(AssistenciaMutua, id)
    if not assistencia:
        raise HTTPException(status_code=404, detail="Assistência não encontrada")

    assistido = await db.get(ContactoProfessor, dados.professor_assistido_id)
    assistente = await db.get(ContactoProfessor, dados.professor_assistente_id)

    # Verificar se ambos os registros foram encontrados
    if not assistido:
        raise HTTPException(status_code=404, detail="Professor assistido não encontrado")
    if not assistente:
        raise HTTPException(status_code=404, detail="Professor assistente não encontrado")

    # Atualizar dados da assistência
    assistencia.professor_assistido_nome = assistido.nome
    assistencia.professor_assistente_nome = assistente.nome
    assistencia.classe = dados.classe
    assistencia.turma = dados.turma
    assistencia.disciplina = dados.disciplina
    assistencia.numero_sala = dados.numero_sala
    assistencia.localizacao_sala = dados.localizacao_sala
    assistencia.trimestre = dados.trimestre
    assistencia.data_hora = dados.data_hora

    await db.commit()
    await db.refresh(assistencia)
    return assistencia

# -----------------------------
# Deletar assistência por ID
# -----------------------------
@router.delete("/id/{id}")
async def deletar_assistencia(id: int, db: AsyncSession = Depends(get_db)):
    assistencia = await db.get(AssistenciaMutua, id)
    if not assistencia:
        raise HTTPException(status_code=404, detail="Assistência não encontrada")
    await db.delete(assistencia)
    await db.commit()
    return {"message": "Assistência deletada com sucesso"}