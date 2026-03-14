from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.assistencia_direcao import AssistenciaDirecao
from models.contactos_professores import ContactoProfessor
from models.contactos_diretor import ContactoDiretor
from schemas.assistencia_direcao import AssistenciaDirecaoCreate
from pydantic import BaseModel
import traceback

router = APIRouter(
    prefix="/assistencias-direcao",
    tags=["Assistências Direção"]
)

# =========================
# LISTAR TODAS ASSISTÊNCIAS
# =========================
@router.get("/")
async def listar_assistencias(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(AssistenciaDirecao))
        assistencias = result.scalars().all()
        return assistencias
    except Exception as e:
        print("Erro listar_assistencias:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# =========================
# LISTAR PROFESSORES
# =========================
@router.get("/professores")
async def listar_professores(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ContactoProfessor.nome))
        professores = [p[0] for p in result.all()]
        if not professores:
            print("Atenção: Nenhum professor encontrado")
        return professores
    except Exception as e:
        print("Erro listar_professores:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# =========================
# LISTAR DIRETORES
# =========================
@router.get("/diretores")
async def listar_diretores(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ContactoDiretor.nome))
        diretores = [d[0] for d in result.all()]
        if not diretores:
            print("Atenção: Nenhum diretor encontrado")
        return diretores
    except Exception as e:
        print("Erro listar_diretores:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# =========================
# CRIAR NOVA ASSISTÊNCIA
# =========================
@router.post("/")
async def criar_assistencia(dados: AssistenciaDirecaoCreate, db: AsyncSession = Depends(get_db)):
    try:
        nova = AssistenciaDirecao(**dados.dict())
        db.add(nova)
        await db.commit()
        await db.refresh(nova)
        return nova
    except Exception as e:
        print("Erro criar_assistencia:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# =========================
# OBTER ASSISTÊNCIA POR ID
# =========================
@router.get("/id/{id}")
async def obter_assistencia(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(AssistenciaDirecao).filter_by(id=id))
        ass = result.scalars().first()
        if not ass:
            raise HTTPException(status_code=404, detail="Assistência não encontrada")
        return ass
    except Exception as e:
        print("Erro obter_assistencia:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# =========================
# ATUALIZAR ASSISTÊNCIA
# =========================
@router.put("/id/{id}")
async def atualizar_assistencia(id: int, dados: AssistenciaDirecaoCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(AssistenciaDirecao).filter_by(id=id))
        ass = result.scalars().first()
        if not ass:
            raise HTTPException(status_code=404, detail="Assistência não encontrada")
        for key, value in dados.dict().items():
            setattr(ass, key, value)
        await db.commit()
        await db.refresh(ass)
        return ass
    except Exception as e:
        print("Erro atualizar_assistencia:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# =========================
# DELETAR ASSISTÊNCIA
# =========================
@router.delete("/id/{id}")
async def deletar_assistencia(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(AssistenciaDirecao).filter_by(id=id))
        ass = result.scalars().first()
        if not ass:
            raise HTTPException(status_code=404, detail="Assistência não encontrada")
        await db.delete(ass)
        await db.commit()
        return {"ok": True}
    except Exception as e:
        print("Erro deletar_assistencia:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# =========================
# APROVAR/DESAPROVAR TRIMESTRE GLOBAL
# =========================
class AprovarTrimestreSchema(BaseModel):
    trimestre: str  # "1", "2" ou "3"
    status: str  # "APROVADO" ou "NAO"

@router.put("/aprovar-trimestre")
async def aprovar_trimestre_global(dados: AprovarTrimestreSchema, db: AsyncSession = Depends(get_db)):
    try:
        trimestre = dados.trimestre
        status = dados.status.upper()
        if status not in ["APROVADO", "NAO"]:
            raise HTTPException(status_code=400, detail="Status inválido")

        result = await db.execute(select(AssistenciaDirecao).filter_by(trimestre=trimestre))
        registros = result.scalars().all()
        if not registros:
            print(f"Atenção: Nenhum registro encontrado para o {trimestre}º trimestre")
            raise HTTPException(status_code=404, detail=f"Nenhum registro encontrado para o {trimestre}º trimestre")

        for reg in registros:
            reg.status_aprovacao = status
            db.add(reg)

        await db.commit()
        return {"ok": True, "trimestre": trimestre, "status": status}
    except Exception as e:
        print("Erro aprovar_trimestre_global:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
