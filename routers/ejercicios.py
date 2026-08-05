from decimal import Decimal

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.clase0_ejercicios import ejercicios_clase0
from services.clase1_ejercicios import ejercicios_clase1
from services.psets import ejercicio_por_id, todos_los_psets
from services.validador_ejercicio import probar_ejercicio
from templating import templates

router = APIRouter()


def _jsonable(obj):
    """Convierte Decimal y otros tipos no serializables a tipos JSON-safe."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    return obj


def _todos_los_ejercicios() -> dict[str, object]:
    out: dict[str, object] = {}
    for e in ejercicios_clase0():
        out[e.id] = e
    for e in ejercicios_clase1():
        out[e.id] = e
    for lista in todos_los_psets().values():
        for e in lista:
            out[e.id] = e
    return out


@router.get("/clase0", response_class=HTMLResponse)
async def ejercicios_c0(request: Request):
    return templates.TemplateResponse(
        request,
        "ejercicios.html",
        {
            "clase_num": 0,
            "clase_titulo": "Consultas",
            "ejercicios": ejercicios_clase0(),
        },
    )


@router.get("/clase1", response_class=HTMLResponse)
async def ejercicios_c1(request: Request):
    return templates.TemplateResponse(
        request,
        "ejercicios.html",
        {
            "clase_num": 1,
            "clase_titulo": "Relaciones",
            "ejercicios": ejercicios_clase1(),
        },
    )


@router.post("/probar/{ejercicio_id}")
async def probar_ejercicio_endpoint(
    request: Request,
    ejercicio_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Prueba la SQL del usuario contra la SQL esperada del ejercicio.

    Body: {"sql": "..."} (JSON o form-data).
    Respuesta: {ok, mensaje, error, columnas_esperadas, filas_esperadas,
                columnas_obtenidas, filas_obtenidas, coinciden_columnas, coinciden_filas}
    """
    ejercicios = _todos_los_ejercicios()
    ejercicio = ejercicios.get(ejercicio_id)
    if ejercicio is None:
        return JSONResponse(
            {"ok": False, "mensaje": "no-found", "error": "Ejercicio no encontrado"},
            status_code=404,
        )

    sql_usuario = await _extraer_sql(request)
    if not sql_usuario.strip():
        return JSONResponse(
            {"ok": False, "mensaje": "empty", "error": "Consulta vacia"},
            status_code=400,
        )

    resultado = await probar_ejercicio(
        db=db,
        sql_usuario=sql_usuario,
        sql_esperado=ejercicio.sql,
        orden_importa=ejercicio.orden_importa,
        esquema=ejercicio.esquema,
    )

    return JSONResponse({
        "ok": resultado.ok,
        "mensaje": resultado.mensaje,
        "error": resultado.error,
        "diagnostico": resultado.diagnostico,
        "coinciden_columnas": resultado.coinciden_columnas,
        "coinciden_filas": resultado.coinciden_filas,
        "columnas_esperadas": resultado.columnas_esperadas,
        "filas_esperadas": _jsonable(resultado.filas_esperadas),
        "columnas_obtenidas": resultado.columnas_obtenidas,
        "filas_obtenidas": _jsonable(resultado.filas_obtenidas),
    })


async def _extraer_sql(request: Request) -> str:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            return str(body.get("sql", ""))
        except Exception:
            return ""
    form = await request.form()
    return str(form.get("sql", ""))