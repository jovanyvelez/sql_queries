"""Ruta /cheatsheet — referencia SQL rápida (sin soluciones de ejercicios)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from services.cheatsheet import CHEATSHEET
from templating import templates

router = APIRouter()


@router.get("/cheatsheet", response_class=HTMLResponse)
async def cheatsheet(request: Request):
    return templates.TemplateResponse(
        request,
        "cheatsheet.html",
        {"cheatsheet": CHEATSHEET},
    )