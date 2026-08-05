from urllib.parse import unquote
from decimal import Decimal

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.rate_limit import limitar_consulta
from services.validador_sql import extraer_search_path, validar_consulta
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

# Esquemas disponibles en el dropdown de la consola
ESQUEMAS_CONSOLA = [
    ("public", "Curso (public) — sql_teach"),
    ("dese", "Problem Set — DESE"),
    ("moneyball", "Problem Set — Moneyball"),
    ("packages", "Problem Set — Packages, Please"),
]


@router.get("/consola", response_class=HTMLResponse)
async def consola_get(
    request: Request,
    sql: str = Query(""),
    esquema: str = Query("public"),
):
    return templates.TemplateResponse(
        request,
        "consola.html",
        {
            "error": None,
            "resultado": None,
            "sql_anterior": unquote(sql) if sql else None,
            "esquemas": ESQUEMAS_CONSOLA,
            "esquema_actual": esquema if esquema in dict(ESQUEMAS_CONSOLA) else "public",
        },
    )


async def _ejecutar_consola(db: AsyncSession, sql: str, esquema: str | None):
    """Ejecuta una consulta de solo lectura, aplicando SET search_path si hace falta.

    Devuelve (resultado, error). `resultado` es lista[dict] o None.
    """
    try:
        consulta = validar_consulta(sql)
    except Exception as e:
        return None, str(e)
    # Extraer search_path del prefijo (si el usuario lo escribió a mano)
    esquema_prefijo, consulta_sin_prefijo = extraer_search_path(consulta)
    esquema_final = esquema_prefijo or esquema or "public"
    async with db.begin() as tx:
        await db.execute(text("SET TRANSACTION READ ONLY"))
        if esquema_final and esquema_final != "public":
            await db.execute(
                text(f'SET search_path TO "{esquema_final}", public')
            )
        result = await db.execute(text(consulta_sin_prefijo))
        if result.returns_rows:
            filas = result.mappings().all()
            resultado = [dict(f) for f in filas[:50]]
        else:
            resultado = [
                {"mensaje": "Consulta ejecutada correctamente (sin filas de retorno)."}
            ]
        await tx.rollback()
    return resultado, None


@router.post("/consulta", response_class=HTMLResponse)
async def ejecutar_consulta_usuario(
    request: Request,
    db: AsyncSession = Depends(get_db),
    sql: str = Form(""),
    esquema: str = Form("public"),
    _rate: None = Depends(limitar_consulta),
):
    if not sql.strip():
        return templates.TemplateResponse(
            request,
            "consola.html",
            {
                "error": None,
                "resultado": None,
                "sql_anterior": None,
                "esquemas": ESQUEMAS_CONSOLA,
                "esquema_actual": esquema or "public",
            },
        )

    resultado, error = await _ejecutar_consola(db, sql, esquema)

    return templates.TemplateResponse(
        request,
        "consola.html",
        {
            "error": error,
            "resultado": resultado,
            "sql_anterior": sql,
            "esquemas": ESQUEMAS_CONSOLA,
            "esquema_actual": esquema or "public",
        },
    )


@router.post("/consulta/api")
async def ejecutar_consulta_api(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(limitar_consulta),
):
    """Ejecuta una consulta SQL y devuelve el resultado como JSON.

    Payload: {"sql": "...", "esquema": "public|dese|moneyball|packages"}
    Respuesta: {"ok": bool, "columns": [...], "rows": [...], "elapsed_ms": int, "error": str|null}
    """
    payload = await _extraer_payload(request)
    sql = payload.get("sql", "")
    esquema = payload.get("esquema", "public")
    if not sql.strip():
        return JSONResponse(
            {"ok": False, "error": "La consulta esta vacia", "columns": [], "rows": [], "elapsed_ms": 0},
            status_code=400,
        )

    import time as _time

    t0 = _time.perf_counter()
    try:
        consulta = validar_consulta(sql)
        esquema_prefijo, consulta_sin_prefijo = extraer_search_path(consulta)
        esquema_final = esquema_prefijo or esquema or "public"
        async with db.begin() as tx:
            await db.execute(text("SET TRANSACTION READ ONLY"))
            if esquema_final and esquema_final != "public":
                await db.execute(text(f'SET search_path TO "{esquema_final}", public'))
            result = await db.execute(text(consulta_sin_prefijo))
            if result.returns_rows:
                filas = result.mappings().all()
                columnas = list(filas[0].keys()) if filas else []
                filas_dict = [dict(f) for f in filas[:50]]
            else:
                columnas = ["mensaje"]
                filas_dict = [{"mensaje": "Consulta ejecutada correctamente (sin filas de retorno)."}]
            await tx.rollback()
        elapsed = round((_time.perf_counter() - t0) * 1000, 2)
        return JSONResponse({
            "ok": True,
            "columns": columnas,
            "rows": _jsonable(filas_dict),
            "row_count": len(filas_dict),
            "truncated": result.returns_rows and len(filas_dict) == 50,
            "elapsed_ms": elapsed,
            "error": None,
        })
    except Exception as e:
        elapsed = round((_time.perf_counter() - t0) * 1000, 2)
        return JSONResponse(
            {"ok": False, "error": str(e), "columns": [], "rows": [], "elapsed_ms": elapsed},
            status_code=200,
        )


async def _extraer_payload(request: Request) -> dict[str, str]:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            return {"sql": str(body.get("sql", "")), "esquema": str(body.get("esquema", "public"))}
        except Exception:
            return {"sql": "", "esquema": "public"}
    form = await request.form()
    return {
        "sql": str(form.get("sql", "")),
        "esquema": str(form.get("esquema", "public")),
    }


async def _extraer_sql(request: Request) -> str:
    """Retrocompatibilidad: devuelve solo el sql (para clientes antiguos)."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            return str(body.get("sql", ""))
        except Exception:
            return ""
    form = await request.form()
    return str(form.get("sql", ""))
