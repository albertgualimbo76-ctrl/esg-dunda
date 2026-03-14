from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/chefe_secretaria", response_class=HTMLResponse)
async def chefe_secretaria(request: Request):
    return templates.TemplateResponse(
        "chefe_secretaria.html",
        {"request": request}
    )
