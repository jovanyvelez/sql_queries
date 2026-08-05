"""Ruta /cheatsheet — cheatsheet SQL de referencia + todas las soluciones."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from services.cheatsheet import CHEATSHEET, grupos_de_soluciones, total_ejercicios
from templating import templates

router = APIRouter()


@router.get("/cheatsheet", response_class=HTMLResponse)
async def cheatsheet(request: Request):
    return templates.TemplateResponse(
        request,
        "cheatsheet.html",
        {
            "cheatsheet": CHEATSHEET,
            "grupos": grupos_de_soluciones(),
            "total": total_ejercicios(),
        },
    )