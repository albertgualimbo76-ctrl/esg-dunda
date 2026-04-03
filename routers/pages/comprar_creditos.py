from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/comprar_creditos", response_class=HTMLResponse)
async def dados_aluno(request: Request):
    return templates.TemplateResponse(
        "comprar_creditos.html",
        {"request": request}
    )
