from urllib.parse import unquote

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.rate_limit import limitar_consulta
from services.validador_sql import validar_consulta
from templating import templates

router = APIRouter()


@router.get("/consola", response_class=HTMLResponse)
async def consola_get(request: Request, sql: str = Query("")):
    return templates.TemplateResponse(
        request,
        "consola.html",
        {
            "error": None,
            "resultado": None,
            "sql_anterior": unquote(sql) if sql else None,
        },
    )


@router.post("/consulta", response_class=HTMLResponse)
async def ejecutar_consulta_usuario(
    request: Request,
    db: AsyncSession = Depends(get_db),
    sql: str = Form(""),
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
            },
        )

    error = None
    resultado = None
    try:
        consulta = validar_consulta(sql)
        async with db.begin() as tx:
            await db.execute(text("SET TRANSACTION READ ONLY"))
            result = await db.execute(text(consulta))
            if result.returns_rows:
                filas = result.mappings().all()
                resultado = [dict(f) for f in filas[:50]]
            else:
                resultado = [
                    {
                        "mensaje": "Consulta ejecutada correctamente (sin filas de retorno)."
                    }
                ]
            await tx.rollback()
    except Exception as e:
        error = str(e)

    return templates.TemplateResponse(
        request,
        "consola.html",
        {
            "error": error,
            "resultado": resultado,
            "sql_anterior": sql,
        },
    )


@router.post("/consulta/api")
async def ejecutar_consulta_api(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(limitar_consulta),
):
    """Ejecuta una consulta SQL y devuelve el resultado como JSON.

    Payload: {"sql": "..."} (form-data o JSON).
    Respuesta: {"ok": bool, "columns": [...], "rows": [...], "elapsed_ms": int, "error": str|null}
    """
    sql = await _extraer_sql(request)
    if not sql.strip():
        return JSONResponse(
            {"ok": False, "error": "La consulta esta vacia", "columns": [], "rows": [], "elapsed_ms": 0},
            status_code=400,
        )

    import time as _time

    t0 = _time.perf_counter()
    try:
        consulta = validar_consulta(sql)
        async with db.begin() as tx:
            await db.execute(text("SET TRANSACTION READ ONLY"))
            result = await db.execute(text(consulta))
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
            "rows": filas_dict,
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
