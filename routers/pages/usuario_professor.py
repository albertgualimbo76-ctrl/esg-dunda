from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/usuario_professor", response_class=HTMLResponse)
async def usuario_professor(request: Request):
    return templates.TemplateResponse(
        "usuario_professor.html",
        {"request": request}
    )
