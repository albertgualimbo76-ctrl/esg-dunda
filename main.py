# main.py
import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import mozesms

# Banco de dados
from database import Base, engine

# Routers API e Pages
from routers import (
    professor, aluno, classe, turma, matricula, admin, dap,
    director, chefe_secretaria, funcionario_secretaria, usuario_professor,
    dashboard, importar_alunos, sms, encontro, contactos, assistencias, mozesms
)
from routers.mozesms import comprar_creditos
from routers.pages import ep_phandira_2, dados_aluno, encontros, contacto, informacoes, assistencia, ass_direccao, comprar_creditos
from routers.assistencia_direcao import router as assistencia_direcao_router

# 🔥 Monitores automáticos
from services.monitor_encontros import monitorar_encontros
from services.monitorar_assistencias import monitorar_assistencias
from services.monitor_ass_direcao import monitorar_assistencias_direcao as monitor_ass_direcao

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
        "https://ep-phandira-2.onrender.com"
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
    return RedirectResponse(url="/ep_phandira_2")

# ==========================
# API routes (sem prefixo /api)
# ==========================
app.include_router(professor.router)  # /professor
app.include_router(assistencia_direcao_router)  # /assistencias-direcao
app.include_router(aluno.router)  # /aluno
app.include_router(classe.router)  # /classe
app.include_router(turma.router)  # /turma
app.include_router(matricula.router)  # /matricula
app.include_router(admin.router)  # /admin
app.include_router(dap.router)  # /dap
app.include_router(director.router)  # /director
app.include_router(chefe_secretaria.router)  # /chefe_secretaria
app.include_router(funcionario_secretaria.router)  # /funcionario_secretaria
app.include_router(usuario_professor.router)  # /usuario_professor
app.include_router(dashboard.router)  # /dashboard
app.include_router(importar_alunos.router)  # /importar_alunos
app.include_router(sms.router)  # /sms
app.include_router(encontro.router)  # /encontro
app.include_router(contactos.router)  # /contactos
app.include_router(encontros.router)  # /encontros
app.include_router(contacto.router)  # /contacto
app.include_router(informacoes.router)  # /informacoes
app.include_router(assistencias.router)  # /assistencias
app.include_router(assistencia.router)  # /assistencia
app.include_router(ass_direccao.router)  # /ass_direccao
app.include_router(mozesms.router)

# ==========================
# HTML pages
# ==========================
app.include_router(ep_phandira_2.router)
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
app.include_router(comprar_creditos.router)

# ==========================
# Fim do main.py
# ==========================
