from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/dap", response_class=HTMLResponse)
async def dap(request: Request):
    return templates.TemplateResponse(
        "dap.html",
        {"request": request}
    )
