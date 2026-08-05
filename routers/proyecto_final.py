"""Ruta /proyecto-final — enunciado del proyecto final de CS50 SQL traducido."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from templating import templates

router = APIRouter()


@router.get("/proyecto-final", response_class=HTMLResponse)
async def proyecto_final(request: Request):
    return templates.TemplateResponse(
        request,
        "proyecto_final.html",
        {},
    )