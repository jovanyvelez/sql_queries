from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from services.modulos import (
    curso_anterior_modulo,
    curso_siguiente_modulo,
    curso_titulo,
    obtener_modulo,
    obtener_modulos,
)
from templating import templates

router = APIRouter()


@router.get("/clase0")
async def clase0_redirect():
    return RedirectResponse(url="/clases/consultas", status_code=301)


@router.get("/clase1")
async def clase1_redirect():
    return RedirectResponse(url="/clases/relaciones", status_code=301)


@router.get("/{curso}", response_class=HTMLResponse)
async def curso_index(request: Request, curso: str):
    if curso not in ("consultas", "relaciones"):
        return RedirectResponse(url="/", status_code=301)
    modulos = obtener_modulos(curso)
    return templates.TemplateResponse(
        request,
        "curso_index.html",
        {
            "curso": curso,
            "curso_titulo": curso_titulo(curso),
            "modulos": modulos,
        },
    )


@router.get("/{curso}/{slug}", response_class=HTMLResponse)
async def modulo_detalle(request: Request, curso: str, slug: str):
    if curso not in ("consultas", "relaciones"):
        return RedirectResponse(url="/", status_code=301)
    modulo = obtener_modulo(curso, slug)
    if modulo is None:
        return RedirectResponse(url=f"/clases/{curso}", status_code=301)
    return templates.TemplateResponse(
        request,
        "modulo.html",
        {
            "curso": curso,
            "curso_titulo": curso_titulo(curso),
            "modulos": obtener_modulos(curso),
            "modulo": modulo,
            "anterior": curso_anterior_modulo(curso, slug),
            "siguiente": curso_siguiente_modulo(curso, slug),
        },
    )