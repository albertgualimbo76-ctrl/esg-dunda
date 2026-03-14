from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/assistencia", response_class=HTMLResponse)
async def assistencia(request: Request):
    return templates.TemplateResponse(
        "assistencia.html",
        {"request": request}
    )
