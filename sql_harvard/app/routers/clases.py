from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.templating import templates

router = APIRouter()


@router.get("/clase0", response_class=HTMLResponse)
async def clase0(request: Request):
    return templates.TemplateResponse(request, "clase0.html")


@router.get("/clase1", response_class=HTMLResponse)
async def clase1(request: Request):
    return templates.TemplateResponse(request, "clase1.html")
