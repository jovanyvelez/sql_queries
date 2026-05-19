# PROYECTO.md — Aplicacion Web de Consultas SQL

## Descripcion

Aplicacion web construida con **FastAPI + Jinja2 + SQLAlchemy + asyncpg** que sirve
como plataforma educativa para el curso CS50 SQL de Harvard adaptado a PostgreSQL
y traducido al espanol. Incluye contenido estatico de las clases, ejercicios
interactivos con hoja de respuestas y una consola SQL para ejecutar consultas
contra la base de datos real.

Desplegable en **Vercel** (capa gratuita), usa **Neon** como PostgreSQL en la nube
para evitar instalaciones locales.

---

## Indice

1. [Estructura del proyecto](#estructura-del-proyecto)
2. [Arquitectura](#arquitectura)
3. [Capa de datos — `database.py`](#capa-de-datos--databasepy)
4. [Capa de servicios — `services/`](#capa-de-servicios--services)
5. [Capa de rutas — `routers/`](#capa-de-rutas--routers)
6. [Plantillas — `templates/`](#plantillas--templates)
7. [Sanitizacion y rate limiting](#sanitizacion-y-rate-limiting)
8. [Keep-alive para Neon](#keep-alive-para-neon)
9. [Ejecucion y despliegue](#ejecucion-y-despliegue)
10. [Como extender el proyecto](#como-extender-el-proyecto)

---

## Estructura del proyecto

```
app/
├── main.py                  # FastAPI app, lifespan, healthcheck, ruta /
├── templating.py            # Jinja2Templates compartido entre routers
├── database.py              # Conexion a PostgreSQL via SQLAlchemy async
├── pyproject.toml           # Dependencias (uv)
├── requirements.txt         # Dependencias (pip / Vercel)
├── .env-sample              # Plantilla de variables de entorno
├── datos.sql                # Dump completo de la BD (esquema + datos)
├── LICENSE                  # MIT
├── CONTRIBUTING.md          # Guia de contribucion
├── routers/
│   ├── clases.py            # GET /clase0, /clase1
│   ├── ejercicios.py        # GET /ejercicios/clase{0,1}, /respuestas
│   └── consola.py           # GET /consola, POST /consulta
├── services/
│   ├── ejercicios.py        # Dataclass Ejercicio
│   ├── clase0_ejercicios.py # 35 ejercicios de Clase 0
│   ├── clase1_ejercicios.py # 32 ejercicios de Clase 1
│   ├── keep_alive.py        # Ping cada 4 min (Neon capa gratuita)
│   ├── rate_limit.py        # Rate limiter para /consulta
│   └── validador_sql.py     # Bloquea INSERT/UPDATE/DELETE/DROP/...
├── templates/
│   ├── base.html            # Layout comun + nav
│   ├── index.html           # Pagina de inicio
│   ├── clase0.html          # Clase 0 (HTML estatico desde .md)
│   ├── clase1.html          # Clase 1 (HTML estatico desde .md)
│   ├── ejercicios.html      # Lista de ejercicios
│   ├── respuestas.html      # Hoja de respuestas
│   ├── consola.html         # Consola SQL interactiva
│   └── 500.html             # Pagina de error 500
└── static/
    ├── estilos.css          # CSS unificado (modo oscuro)
    └── images/              # Imagenes del curso
```

---

## Arquitectura

El proyecto sigue el patron de **tres capas**:

```
┌──────────────────────────────────────────────────┐
│  Routers (Presentation)                          │
│  routers/ + templates/                           │
│  - Definen endpoints HTTP                        │
│  - Renderizan Jinja2                             │
│  - Sin logica de negocio ni acceso directo a BD  │
└──────────────────┬───────────────────────────────┘
                   │  importan
┌──────────────────▼───────────────────────────────┐
│  Services (Business)                             │
│  services/                                       │
│  - Logica de ejercicios, validacion, rate limit  │
│  - No conocen HTTP ni plantillas                 │
└──────────────────┬───────────────────────────────┘
                   │  usan
┌──────────────────▼───────────────────────────────┐
│  Data (database.py)                              │
│  - Engine asincrono de SQLAlchemy                │
│  - Pool de conexiones a PostgreSQL (Neon)        │
│  - Dependency injection via get_db()             │
└──────────────────────────────────────────────────┘
```

Los **templates de clase** (`clase0.html`, `clase1.html`) son HTML estatico
generado una vez desde los archivos `.md` mediante `convertir_md.py`. No hay
conversion markdown en runtime.

---

## Capa de datos — `database.py`

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

load_dotenv(Path(__file__).parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://profesor:profesor@localhost/sql_teach")

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=5, max_overflow=10)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

- La URL se lee de la variable de entorno `DATABASE_URL` (`.env` en local,
  Vercel env vars en produccion).
- Fallback a `localhost` si no esta definida.
- `expire_on_commit=False` evita que SQLAlchemy recalcule atributos tras
  un commit, necesario en aplicaciones asincronas.
- `get_db()` es un **generador asincrono** que FastAPI usa como dependencia
  (`Depends`). La sesion se cierra automaticamente al terminar la peticion.

---

## Capa de servicios — `services/`

### `ejercicios.py` — Dataclass

```python
@dataclass
class Ejercicio:
    id: str
    numero: int
    titulo: str
    enunciado: str
    dificultad: str      # "basico", "intermedio", "avanzado"
    sql: str              # Consulta SQL (respuesta)
    params: dict[str, Any] = field(default_factory=dict)
```

Cada ejercicio tiene un `id`, un `numero`, un `enunciado` que describe el
problema, y la `sql` con la respuesta. Las plantillas usan `dificultad`
para colorear las tarjetas (verde/amarillo/rojo).

### `validador_sql.py` — Solo lectura

Bloquea cualquier sentencia que no sea `SELECT`, `WITH` o `EXPLAIN`.
Elimina comentarios y literales de cadena antes de analizar, evita
multiples sentencias (`;`) y rechaza palabras clave peligrosas
(`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, etc.).

### `rate_limit.py` — Limite de consultas

Implementa un sliding window en memoria: maximo 10 consultas por minuto
por direccion IP. Si se excede, devuelve HTTP 429.

### `keep_alive.py` — Ping a Neon

La capa gratuita de Neon suspende la base de datos tras inactividad.
Cada 4 minutos se ejecuta `SELECT 1` para mantenerla activa.
Se ejecuta como tarea asincrona dentro del `lifespan` de FastAPI.

---

## Capa de rutas — `routers/`

Las rutas estan agrupadas por funcion usando `APIRouter`:

| Router | Rutas |
|---|---|
| `clases.py` | `GET /clase0`, `GET /clase1` |
| `ejercicios.py` | `GET /ejercicios/clase0`, `/ejercicios/clase0/respuestas`, `/ejercicios/clase1`, `/ejercicios/clase1/respuestas` |
| `consola.py` | `GET /consola`, `POST /consulta` |

`main.py` solo contiene `GET /`, `GET /health` y el `exception_handler` para 500.

### `POST /consulta` — flujo completo

```
1. Navegador ──POST /consulta──▶ FastAPI
2. Depends(limitar_consulta) → verifica rate limit por IP
3. Depends(get_db) → crea AsyncSession
4. validar_consulta(sql) → rechaza si no es SELECT/WITH/EXPLAIN
5. db.begin() → inicia transaccion explicita
6. SET TRANSACTION READ ONLY → proteccion a nivel BD
7. db.execute(text(consulta)) → ejecuta la consulta
8. result.mappings().all() → convierte filas a dicts (max 50)
9. tx.rollback() → siempre rollback, nunca commit
10. Jinja2 renderiza consola.html con resultados o error
```

---

## Plantillas — `templates/`

Herencia de plantillas:

```
base.html                         (layout, nav, <link rel="stylesheet">)
├── index.html                    (inicio)
├── clase0.html                   (clase 0 — HTML estatico)
├── clase1.html                   (clase 1 — HTML estatico)
├── ejercicios.html               (lista de ejercicios)
├── respuestas.html               (hoja de respuestas)
├── consola.html                  (consola SQL)
└── 500.html                      (error 500)
```

- `base.html` define nav, container, y carga `static/estilos.css`.
- `consola.html` extiende `base.html` y sobrescribe `.container` para ser
  mas ancho (1200px vs 860px).
- Todo el CSS esta en un solo archivo `static/estilos.css` (modo oscuro).
- Mermaid.js se carga desde CDN para los diagramas ER de la Clase 1.

### `base.html` — Layout

Define dos bloques principales:
- `{% block title %}` — titulo de la pagina
- `{% block content %}` — contenido inyectado por cada template
- `{% block extra_css %}` — CSS adicional por pagina (consola)
- `{% block extra_js %}` — JavaScript adicional (Ctrl+Enter en consola)

---

## Sanitizacion y rate limiting

Tres capas de proteccion en `POST /consulta`:

1. **Rate limit** — 10 consultas/min por IP (`services/rate_limit.py`)
2. **Validador SQL** — solo `SELECT`/`WITH`/`EXPLAIN`, bloquea `;` y
   palabras peligrosas (`services/validador_sql.py`)
3. **Transaccion READ ONLY** — `SET TRANSACTION READ ONLY` antes de
   ejecutar, con rollback obligatorio

---

## Keep-alive para Neon

La capa gratuita de Neon suspende la base de datos tras ~5 minutos de
inactividad. El `lifespan` de FastAPI lanza una tarea asincrona que
ejecuta `SELECT 1` cada 4 minutos:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    tarea = asyncio.create_task(mantener_base_de_datos_viva())
    yield
    tarea.cancel()
```

---

## Ejecucion y despliegue

### Local

```bash
cd sql_harvard/app
cp .env-sample .env   # editar con tu DATABASE_URL
uv run fastapi dev main.py
```

### Vercel

1. Conecta el repositorio en Vercel
2. Root directory: `sql_harvard/app`
3. Agrega `DATABASE_URL` en Environment Variables
4. Deploy

---

## Como extender el proyecto

### Agregar una nueva clase (Clase 2)

1. Crear `CS50_SQL_Clase2_Diseno.md` con el contenido traducido.
2. Ejecutar `convertir_md.py` (modificar `ARCHIVOS` para incluir clase 2).
3. Agregar ruta en `routers/clases.py` que sirva `clase2.html`.
4. Agregar ejercicios en `services/clase2_ejercicios.py`.
5. Agregar rutas de ejercicios en `routers/ejercicios.py`.
6. Agregar enlace en el nav de `base.html`.

---

**Fuente original:** CS50 SQL — Harvard University. https://cs50.harvard.edu/sql/
