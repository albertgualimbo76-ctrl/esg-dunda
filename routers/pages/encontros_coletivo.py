from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/encontros_coletivo", response_class=HTMLResponse)
async def director(request: Request):
    return templates.TemplateResponse(
        "encontro_coletivo.html",
        {"request": request}
    )
