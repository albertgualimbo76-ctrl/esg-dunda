import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Verifica o diretório de trabalho atual (adicione isso para depuração)
print("Caminho de trabalho:", os.getcwd())  # Verifica o diretório onde o servidor está sendo executado

# Usando caminho absoluto para garantir que o Render encontre o diretório corretamente
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "templates"))

router = APIRouter()

@router.get("/ass_direccao", response_class=HTMLResponse)
async def ass_direccao(request: Request):
    # Retorna o template correto
    return templates.TemplateResponse("ass_direccao.html", {"request": request})