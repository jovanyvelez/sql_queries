from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.services.clase0_ejercicios import ejercicios_clase0
from app.services.clase1_ejercicios import ejercicios_clase1
from app.templating import templates

router = APIRouter()


@router.get("/ejercicios/clase0", response_class=HTMLResponse)
async def ejercicios_c0(request: Request):
    return templates.TemplateResponse(request, "ejercicios.html", {
        "clase_num": 0, "clase_titulo": "Consultas",
        "ejercicios": ejercicios_clase0(),
    })


@router.get("/ejercicios/clase0/respuestas", response_class=HTMLResponse)
async def respuestas_c0(request: Request):
    return templates.TemplateResponse(request, "respuestas.html", {
        "clase_num": 0, "clase_titulo": "Consultas",
        "ejercicios": ejercicios_clase0(),
    })


@router.get("/ejercicios/clase1", response_class=HTMLResponse)
async def ejercicios_c1(request: Request):
    return templates.TemplateResponse(request, "ejercicios.html", {
        "clase_num": 1, "clase_titulo": "Relaciones",
        "ejercicios": ejercicios_clase1(),
    })


@router.get("/ejercicios/clase1/respuestas", response_class=HTMLResponse)
async def respuestas_c1(request: Request):
    return templates.TemplateResponse(request, "respuestas.html", {
        "clase_num": 1, "clase_titulo": "Relaciones",
        "ejercicios": ejercicios_clase1(),
    })
