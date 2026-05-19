import asyncio
import os
import sys
from contextlib import asynccontextmanager

# Garantiza que el directorio del proyecto esté en sys.path,
# tanto en Vercel (script directo) como en local (uvicorn/fastapi dev).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routers import clases, consola, ejercicios
from services.keep_alive import mantener_base_de_datos_viva
from templating import templates


# La capa gratuita de Neon suspende la base de datos tras inactividad.
# Para evitarlo, se ejecuta SELECT 1 cada 4 minutos mientras el servidor esta vivo.
@asynccontextmanager
async def lifespan(app: FastAPI):
    tarea = asyncio.create_task(mantener_base_de_datos_viva())
    yield
    tarea.cancel()


app = FastAPI(title="CS50 SQL — Adaptacion a PostgreSQL", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(clases.router, prefix="/clases")
app.include_router(ejercicios.router, prefix="/ejercicios")
app.include_router(consola.router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/tablas", response_class=HTMLResponse)
async def tablas(request: Request, db: AsyncSession = Depends(get_db)):
    filas = await db.execute(
        text(
            "SELECT table_name, column_name, data_type, is_nullable,"
            " column_default, ordinal_position "
            "FROM information_schema.columns "
            "WHERE table_schema = 'public' "
            "ORDER BY table_name, ordinal_position"
        )
    )
    columnas = filas.fetchall()

    tablas_dict: dict[str, list[dict[str, str]]] = {}
    for col in columnas:
        tn = col.table_name
        if tn not in tablas_dict:
            tablas_dict[tn] = []
        tablas_dict[tn].append(
            {
                "columna": col.column_name,
                "tipo": col.data_type,
                "nulo": "SI" if col.is_nullable == "YES" else "NO",
                "defecto": str(col.column_default) if col.column_default else "—",
            }
        )

    return templates.TemplateResponse(
        request, "tablas.html", {"tablas": tablas_dict}
    )


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return JSONResponse({"status": "ok", "database": "connected"})
    except Exception:
        return JSONResponse(
            {"status": "error", "database": "disconnected"}, status_code=503
        )


@app.exception_handler(500)
async def error_500(request: Request, exc: Exception):
    return templates.TemplateResponse(request, "500.html", status_code=500)
