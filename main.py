# main.py
import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Banco de dados
from database import Base, engine

# Routers API
from routers import (
    professor, aluno, classe, turma, matricula, admin, dap,
    director, chefe_secretaria, funcionario_secretaria, usuario_professor,
    dashboard, importar_alunos, sms, encontro, contactos, assistencias
)
from routers.pages import esg_dunda, dados_aluno, encontros, contacto, informacoes, assistencia, ass_direccao
from routers.assistencia_direcao import router as assistencia_direcao_router

# 🔥 Monitores automáticos
from services.monitor_encontros import monitorar_encontros
from services.monitorar_assistencias import monitorar_assistencias  # monitor antigo
from services.monitor_ass_direcao import monitorar_assistencias_direcao as monitor_ass_direcao  # monitor de direção

# Verifica ambiente
is_production = os.getenv("ENV") == "production"

# Cria app
app = FastAPI(
    title="Sistema de Gestão de SMS",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc"
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://esg-dunda.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ==========================
# Evento startup
# ==========================
@app.on_event("startup")
async def startup():
    # Cria tabelas no banco
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 🔥 Inicia monitores automáticos em background
    asyncio.create_task(monitorar_encontros())
    asyncio.create_task(monitorar_assistencias())
    asyncio.create_task(monitor_ass_direcao())

    print("✅ Sistema iniciado com monitor automático de encontros e assistências")

# ==========================
# Rota raiz → redireciona
# ==========================
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/esg_dunda")

# ==========================
# API routes
# ==========================
app.include_router(professor.router, prefix="/api")
app.include_router(assistencia_direcao_router, prefix="/api")  # Assistências de direção
app.include_router(aluno.router, prefix="/api")
app.include_router(classe.router, prefix="/api")
app.include_router(turma.router, prefix="/api")
app.include_router(matricula.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(dap.router, prefix="/api")
app.include_router(director.router, prefix="/api")
app.include_router(chefe_secretaria.router, prefix="/api")
app.include_router(funcionario_secretaria.router, prefix="/api")
app.include_router(usuario_professor.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(importar_alunos.router, prefix="/api")
app.include_router(sms.router, prefix="/api")
app.include_router(encontro.router, prefix="/api")
app.include_router(contactos.router, prefix="/api")
app.include_router(encontros.router, prefix="/api")
app.include_router(contacto.router, prefix="/api")
app.include_router(informacoes.router, prefix="/api")
app.include_router(assistencias.router, prefix="/api")
app.include_router(assistencia.router, prefix="/api")
app.include_router(ass_direccao.router, prefix="/api")

# ==========================
# HTML pages
# ==========================
app.include_router(esg_dunda.router)
app.include_router(aluno.router)
app.include_router(classe.router)
app.include_router(turma.router)
app.include_router(matricula.router)
app.include_router(admin.router)
app.include_router(dap.router)
app.include_router(director.router)
app.include_router(chefe_secretaria.router)
app.include_router(funcionario_secretaria.router)
app.include_router(usuario_professor.router)
app.include_router(dashboard.router)
app.include_router(dados_aluno.router)
app.include_router(importar_alunos.router)
app.include_router(sms.router)
app.include_router(encontro.router)
app.include_router(contactos.router)
app.include_router(encontros.router)
app.include_router(contacto.router)
app.include_router(informacoes.router)
app.include_router(assistencias.router)
app.include_router(assistencia.router)
app.include_router(ass_direccao.router)

# ==========================
# Fim do main.py
# ==========================
