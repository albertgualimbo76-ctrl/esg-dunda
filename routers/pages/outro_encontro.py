from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/outro_encontro", response_class=HTMLResponse)
async def encontros(request: Request):
    return templates.TemplateResponse(
        "outros_encontros.html",
        {"request": request}
    )
