"""Rutas para los Problem Sets (psets) de CS50 SQL traducidos al español.

Cada pset tiene su propia página con:
  - contexto del problema (historia traducida)
  - link al enunciado original de Harvard
  - link de descarga del ZIP original (dese.zip, moneyball.zip, packages.zip)
  - ejercicios validables (cada estudiante escribe SQL y la app le dice si está bien)
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from services.psets import PSETS_META, pset_por_slug, todos_los_psets
from templating import templates

router = APIRouter()


@router.get("/psets", response_class=HTMLResponse)
async def psets_index(request: Request):
    """Índice de los 3 problem sets disponibles."""
    psets = []
    for slug, meta in PSETS_META.items():
        ejercicios = todos_los_psets().get(slug, [])
        psets.append({**meta, "n_ejercicios": len(ejercicios)})
    return templates.TemplateResponse(
        request,
        "psets_index.html",
        {"psets": psets},
    )


@router.get("/psets/{slug}", response_class=HTMLResponse)
async def pset_detalle(request: Request, slug: str):
    """Página de un pset individual con todos sus ejercicios."""
    meta = PSETS_META.get(slug)
    if meta is None:
        return RedirectResponse(url="/psets", status_code=301)
    ejercicios = pset_por_slug(slug) or []
    return templates.TemplateResponse(
        request,
        "pset_detalle.html",
        {
            "slug": slug,
            "meta": meta,
            "ejercicios": ejercicios,
        },
    )