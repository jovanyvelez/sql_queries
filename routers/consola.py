from urllib.parse import unquote

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.rate_limit import limitar_consulta
from ..services.validador_sql import validar_consulta
from ..templating import templates

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
