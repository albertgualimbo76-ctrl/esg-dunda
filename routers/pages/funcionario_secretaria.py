from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/funcionario_secretaria", response_class=HTMLResponse)
async def funcionario_secretaria(request: Request):
    return templates.TemplateResponse(
        "funcionario_secretaria.html",
        {"request": request}
    )
