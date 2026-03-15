# routers/pages/ass_direccao.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/ass_direccao", response_class=HTMLResponse)
async def ass_direccao(request: Request):
    return templates.TemplateResponse("ass_direccao.html", {"request": request})