import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.keep_alive import mantener_base_de_datos_viva
from templating import templates
from routers import clases, ejercicios, consola


# La capa gratuita de Neon suspende la base de datos tras inactividad.
# Para evitarlo, se ejecuta SELECT 1 cada 4 minutos mientras el servidor esta vivo.
@asynccontextmanager
async def lifespan(app: FastAPI):
    tarea = asyncio.create_task(mantener_base_de_datos_viva())
    yield
    tarea.cancel()


app = FastAPI(title="CS50 SQL — Adaptacion a PostgreSQL", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

app.include_router(clases.router, prefix="/clases")
app.include_router(ejercicios.router, prefix="/ejercicios")
app.include_router(consola.router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return JSONResponse({"status": "ok", "database": "connected"})
    except Exception:
        return JSONResponse({"status": "error", "database": "disconnected"}, status_code=503)


@app.exception_handler(500)
async def error_500(request: Request, exc: Exception):
    return templates.TemplateResponse(request, "500.html", status_code=500)
