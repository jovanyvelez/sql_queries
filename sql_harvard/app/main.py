import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.services.keep_alive import mantener_base_de_datos_viva
from app.templating import templates
from app.routers import clases, ejercicios, consola


# La capa gratuita de Neon suspende la base de datos tras inactividad.
# Para evitarlo, se ejecuta SELECT 1 cada 4 minutos mientras el servidor esta vivo.
@asynccontextmanager
async def lifespan(app: FastAPI):
    tarea = asyncio.create_task(mantener_base_de_datos_viva())
    yield
    tarea.cancel()


app = FastAPI(title="CS50 SQL — Adaptacion a PostgreSQL", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

app.include_router(clases.router)
app.include_router(ejercicios.router)
app.include_router(consola.router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")
