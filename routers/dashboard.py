# routers/dashboard.py
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models.admin import Admin as AdminModel
from models.chefe_secretaria import ChefeSecretaria as ChefeSecretariaModel
from models.dap import DAP as DAPModel
from models.funcionario_secretaria import FuncionarioSecretaria as FuncionarioSecretariaModel
from models.director import Director as DirectorModel
from models.usuario_professor import UsuarioProfessor as UsuarioProfessorModel
from utils.normalizar import normalizar_username
from fastapi.templating import Jinja2Templates

# Caminho onde seus templates HTML estão salvos
templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["dashboard"])


@router.post("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    usuario: str = Form(...),
    senha: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Normaliza o nome
    usuario_normalizado = normalizar_username(usuario)

    # Checa em cada tabela
    result = await db.execute(select(AdminModel).where(AdminModel.nome == usuario_normalizado))
    admin = result.scalar_one_or_none()
    if admin and admin.senha == senha:
        return templates.TemplateResponse("admin.html", {"request": request})

    result = await db.execute(select(ChefeSecretariaModel).where(ChefeSecretariaModel.nome == usuario_normalizado))
    chefe = result.scalar_one_or_none()
    if chefe and chefe.senha == senha:
        return templates.TemplateResponse("chefe_secretaria.html", {"request": request})

    result = await db.execute(select(DAPModel).where(DAPModel.nome == usuario_normalizado))
    dap = result.scalar_one_or_none()
    if dap and dap.senha == senha:
        return templates.TemplateResponse("dap.html", {"request": request})

    result = await db.execute(select(FuncionarioSecretariaModel).where(FuncionarioSecretariaModel.nome == usuario_normalizado))
    funcionario = result.scalar_one_or_none()
    if funcionario and funcionario.senha == senha:
        return templates.TemplateResponse("funcionario_secretaria.html", {"request": request})

    result = await db.execute(select(DirectorModel).where(DirectorModel.nome == usuario_normalizado))
    director = result.scalar_one_or_none()
    if director and director.senha == senha:
        return templates.TemplateResponse("director.html", {"request": request})

    result = await db.execute(select(UsuarioProfessorModel).where(UsuarioProfessorModel.nome == usuario_normalizado))
    usuario_prof = result.scalar_one_or_none()
    if usuario_prof and usuario_prof.senha == senha:
        return templates.TemplateResponse("usuario_professor.html", {"request": request})

    # Se não encontrou em nenhuma tabela
    raise HTTPException(status_code=404, detail="Usuário não encontrado")
