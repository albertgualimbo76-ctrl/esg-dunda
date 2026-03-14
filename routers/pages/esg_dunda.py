from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/esg_dunda", response_class=HTMLResponse)
async def esg_dunda(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )