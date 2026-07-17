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

    tablas_dict: dict[str, list[dict[str, object]]] = {}
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
                "es_pk": False,
                "fk_ref": None,
            }
        )

    # Claves foraneas para el diagrama ER + marca por columna
    relaciones: list[dict[str, str]] = []
    fk_por_columna: dict[tuple[str, str], str] = {}
    pk_por_columna: set[tuple[str, str]] = set()
    try:
        fks = await db.execute(
            text(
                """
                SELECT
                    kcu.table_name AS tabla_origen,
                    kcu.column_name AS columna_origen,
                    ccu.table_name AS tabla_destino,
                    ccu.column_name AS columna_destino
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public'
                ORDER BY kcu.table_name, kcu.column_name
                """
            )
        )
        for r in fks.fetchall():
            relaciones.append(
                {
                    "origen_tabla": r.tabla_origen,
                    "origen_col": r.columna_origen,
                    "destino_tabla": r.tabla_destino,
                    "destino_col": r.columna_destino,
                }
            )
            fk_por_columna[(r.tabla_origen, r.columna_origen)] = (
                f"{r.tabla_destino}.{r.columna_destino}"
            )

        pks = await db.execute(
            text(
                """
                SELECT kcu.table_name, kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_schema = 'public'
                """
            )
        )
        for r in pks.fetchall():
            pk_por_columna.add((r.table_name, r.column_name))
    except Exception:
        pass

    # Marcar PK y FK en cada columna
    for tn, cols in tablas_dict.items():
        for c in cols:
            if (tn, str(c["columna"])) in pk_por_columna:
                c["es_pk"] = True
            ref = fk_por_columna.get((tn, str(c["columna"])))
            if ref:
                c["fk_ref"] = ref

    # Conteo de filas por tabla
    conteos: dict[str, int] = {}
    for tn in tablas_dict:
        try:
            res = await db.execute(text(f'SELECT COUNT(*) FROM "{tn}"'))
            conteos[tn] = int(res.scalar() or 0)
        except Exception:
            conteos[tn] = -1

    return templates.TemplateResponse(
        request,
        "tablas.html",
        {"tablas": tablas_dict, "relaciones": relaciones, "conteos": conteos},
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


TABLAS_ESTADISTICAS = [
    "editoriales", "autores", "traductores", "libros",
    "autoria", "traduccion", "puntuaciones", "lista_larga",
    "leones_marinos", "migraciones",
]


@app.get("/api/estadisticas")
async def estadisticas(db: AsyncSession = Depends(get_db)):
    """Devuelve el número de filas de cada tabla principal."""
    resultados: list[dict[str, object]] = []
    for tabla in TABLAS_ESTADISTICAS:
        try:
            res = await db.execute(text(f'SELECT COUNT(*) AS n FROM "{tabla}"'))
            n = res.scalar()
        except Exception:
            n = None
        resultados.append({"tabla": tabla, "filas": n})
    return JSONResponse({"tablas": resultados})


@app.exception_handler(500)
async def error_500(request: Request, exc: Exception):
    return templates.TemplateResponse(request, "500.html", status_code=500)
