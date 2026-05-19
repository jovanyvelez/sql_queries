# CS50 SQL — Adaptacion a PostgreSQL (en espanol)

Aplicacion web educativa que adapta el curso **CS50's Introduction to Databases with SQL** de Harvard University al espanol, migrando las consultas de SQLite a **PostgreSQL** y exponiendolas a traves de una API web construida con **FastAPI** usando **arquitectura de 3 capas** y **SQL crudo con `text()` de SQLAlchemy**.

---

## Indice

- [Proposito](#proposito)
- [Tecnologias](#tecnologias)
- [Base de datos](#base-de-datos)
- [Ejecutar localmente](#ejecutar-localmente)
- [Arquitectura de 3 capas](#arquitectura-de-3-capas)
  - [Capa 1 — Rutas (Presentacion / Controladores)](#capa-1--rutas-presentacion--controladores)
  - [Capa 2 — Servicios (Logica de negocio)](#capa-2--servicios-logica-de-negocio)
  - [Capa 3 — Datos (Acceso a base de datos)](#capa-3--datos-acceso-a-base-de-datos)
  - [Flujo completo de una peticion](#flujo-completo-de-una-peticion)
- [SQL crudo con `text()` de SQLAlchemy](#sql-crudo-con-text-de-sqlalchemy)
  - [Que es `sqlalchemy.text()`](#que-es-sqlalchemytext)
  - [Como se usa en este proyecto](#como-se-usa-en-este-proyecto)
  - [Transacciones manuales con `begin()` y `rollback()`](#transacciones-manuales-con-begin-y-rollback)
  - [Procesamiento de resultados con `mappings()`](#procesamiento-de-resultados-con-mappings)
  - [El patron `get_db()` — dependencia asincrona de FastAPI](#el-patron-get_db--dependencia-asincrona-de-fastapi)
- [Seguridad](#seguridad)
  - [Validador de SQL](#validador-de-sql)
  - [Rate limiting por IP](#rate-limiting-por-ip)
  - [Transacciones READ ONLY en PostgreSQL](#transacciones-read-only-en-postgresql)
  - [Keep-alive para Neon (PostgreSQL serverless)](#keep-alive-para-neon-postgresql-serverless)
- [Sistema de plantillas Jinja2](#sistema-de-plantillas-jinja2)
- [Conversion de Markdown a HTML](#conversion-de-markdown-a-html)
- [Ejercicios y sistema de auto-evaluacion](#ejercicios-y-sistema-de-auto-evaluacion)
- [Patrones de diseno usados](#patrones-de-diseno-usados)
- [Estructura completa del proyecto](#estructura-completa-del-proyecto)
- [Creditos](#creditos)
- [Licencia](#licencia)

---

## Proposito

El curso **CS50 SQL** de Harvard University ensena bases de datos usando SQLite como motor. Este proyecto lo adapta al espanol y lo migra a PostgreSQL, ofreciendo:

- **Contenido traducido** de las 2 primeras clases (`Clase 0: Consultas` y `Clase 1: Relaciones`), convertido de Markdown a paginas HTML con Jinja2.
- **67 ejercicios interactivos** (35 de Consultas + 32 de Relaciones) con enunciado, indicador de dificultad y hoja de respuestas con las consultas solucion.
- **Consola SQL interactiva** que ejecuta consultas reales contra PostgreSQL, con resultados renderizados en tabla.
- **Modo oscuro** completo desde el CSS unificado.
- **Enfoque didactico** tanto para aprender SQL como para entender como se construye una app web con FastAPI y arquitectura multicapa.

---

## Tecnologias

| Componente | Tecnologia | Proposito en el proyecto |
|---|---|---|
| Backend | Python >= 3.12 | Lenguaje principal |
| Framework web | FastAPI 0.136+ | Enrutamiento, inyeccion de dependencias, lifespan, manejo de errores |
| Servidor ASGI | uvicorn (incluido en `fastapi[standard]`) | Servidor de produccion/desarrollo |
| Base de datos | PostgreSQL (Neon serverless) | Almacenamiento de las 10 tablas del curso (~600k filas en puntuaciones) |
| Driver async | asyncpg 0.31 | Conector asincrono de alto rendimiento entre Python y PostgreSQL |
| SQL toolkit | SQLAlchemy 2.0 | Motor asincrono, gestion de sesiones y construccion de consultas con `text()` |
| Motor de plantillas | Jinja2 (via `fastapi.templating`) | Renderizado de HTML con herencia de templates (`base.html`) |
| CSS | 1 solo archivo (`estilos.css`, ~850 lineas) | Modo oscuro completo (GitHub Dark), responsive, sin frameworks |
| Diagramas | Mermaid.js (CDN) | Diagramas Entidad-Relacion renderizados en el navegador |
| Markdown → HTML | markdown-it-py | Script offline `convertir_md.py` para generar el contenido de las clases |
| Variables de entorno | python-dotenv | Carga de `DATABASE_URL` desde `.env` |

---

## Base de datos

El proyecto usa una base de datos PostgreSQL llamada `sql_teach` con **10 tablas**:

| Tabla | Filas aprox. | Descripcion |
|---|---|---|
| `editoriales` | ~10 | Editoriales de libros |
| `autores` | ~10 | Autores de libros |
| `traductores` | ~10 | Traductores |
| `libros` | ~300 | Libros del Booker Prize (ISBN, titulo, ano, paginas, editorial_id) |
| `autoria` | ~300 | Relacion N:M entre autores y libros (tabla de juntura) |
| `traduccion` | ~300 | Relacion N:M entre traductores y libros |
| `puntuaciones` | **604,173** | Puntuaciones de lectores (libro_id, puntuacion 1-5) |
| `lista_larga` | ~130 | Libros nominados al Booker Prize |
| `leones_marinos` | ~10 | Datos de especie marina (ejemplo didactico para JOIN) |
| `migraciones` | ~10 | Migraciones de leones marinos (ejemplo didactico) |

El archivo `datos.sql` contiene el dump completo (esquema + datos) listo para importar:

```bash
psql -U tu_usuario -d tu_base < datos.sql
```

La base de datos esta alojada en **Neon** (PostgreSQL serverless con capa gratuita). La URL de conexion se configura via variable de entorno `DATABASE_URL` y usa el driver `asyncpg` con SSL requerido:

```
DATABASE_URL=postgresql+asyncpg://usuario:password@host/basedatos?ssl=require
```

---

## Ejecutar localmente

**Requisitos previos:** Python >= 3.12 y `uv` instalado ([instalar uv](https://docs.astral.sh/uv/)).

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd consultas_sql

# Copiar y configurar variables de entorno
cp .env-sample .env
# Editar .env con tu DATABASE_URL real

# Instalar dependencias y ejecutar (uv se encarga de todo)
uv run fastapi dev main.py
```

La aplicacion se sirve en `http://localhost:8000`.

Si no defines `DATABASE_URL`, la aplicacion intentara conectarse a `postgresql+asyncpg://profesor:profesor@localhost/sql_teach` como fallback.

---

## Arquitectura de 3 capas

Este proyecto implementa una **arquitectura de 3 capas** (three-tier architecture), un patron de diseno que separa claramente las responsabilidades en tres niveles independientes. Esta es una de las arquitecturas mas utilizadas en aplicaciones web profesionales porque facilita el mantenimiento, el testing y la escalabilidad.

```
┌───────────────────────────────────────────────────────────────┐
│                    🌐 USUARIO (Navegador)                      │
│            Escribe SQL en la consola, navega por               │
│            las clases, consulta ejercicios...                  │
└────────────────────────┬──────────────────────────────────────┘
                         │  HTTP (GET/POST)
                         ▼
┌───────────────────────────────────────────────────────────────┐
│         CAPA 1 — PRESENTACION (Routers + Templates)            │
│                                                               │
│  routers/clases.py           →  templates/clase{0,1}.html     │
│  routers/ejercicios.py       →  templates/ejercicios.html     │
│                               →  templates/respuestas.html    │
│  routers/consola.py          →  templates/consola.html        │
│  main.py        (/, /health) →  templates/index.html, 500.html│
│  templating.py  (instancia Jinja2Templates compartida)        │
│                                                               │
│  RESPONSABILIDAD: Recibir HTTP, delegar a servicios,          │
│  renderizar HTML con Jinja2, devolver respuestas.             │
│  NUNCA accede directamente a la base de datos                 │
│  (salvo la ruta /health y /consulta via get_db).              │
└────────────────────────┬──────────────────────────────────────┘
                         │  llama a funciones de servicios
                         ▼
┌───────────────────────────────────────────────────────────────┐
│            CAPA 2 — SERVICIOS (Logica de negocio)              │
│                                                               │
│  services/ejercicios.py        →  Dataclass Ejercicio         │
│  services/clase0_ejercicios.py →  35 ejercicios (Consultas)   │
│  services/clase1_ejercicios.py →  32 ejercicios (Relaciones)  │
│  services/validador_sql.py     →  Filtro de SQL peligroso     │
│  services/rate_limit.py        →  Control de abuso por IP     │
│  services/keep_alive.py        →  Ping periodico a BD         │
│                                                               │
│  RESPONSABILIDAD: Contener las reglas del negocio,            │
│  validaciones, estructuras de datos y logica pura.            │
│  NO conoce HTTP, NO conoce HTML, NO renderiza.                │
│  Puede acceder a la capa de datos si necesita consultar.      │
└────────────────────────┬──────────────────────────────────────┘
                         │  usa AsyncSession / text()
                         ▼
┌───────────────────────────────────────────────────────────────┐
│              CAPA 3 — DATOS (Persistencia)                     │
│                                                               │
│  database.py  →  create_async_engine()                        │
│                  async_sessionmaker()                         │
│                  get_db() (generador asincrono)                │
│                                                               │
│  PostgreSQL (Neon serverless)                                 │
│                                                               │
│  RESPONSABILIDAD: Conectarse a la base de datos,              │
│  gestionar el pool de conexiones, proporcionar sesiones       │
│  asincronas. Es la unica capa que conoce la URL de BD.        │
└───────────────────────────────────────────────────────────────┘
```

### Capa 1 — Rutas (Presentacion / Controladores)

Es la **puerta de entrada HTTP**. Cada archivo en `routers/` define un `APIRouter` de FastAPI que agrupa endpoints relacionados. No contienen logica de negocio: reciben la peticion, delegan a los servicios, y devuelven HTML (o JSON).

**Archivo: `routers/clases.py`** — 16 lineas
```python
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from templating import templates

router = APIRouter()

@router.get("/clase0", response_class=HTMLResponse)
async def clase0(request: Request):
    return templates.TemplateResponse(request, "clase0.html")

@router.get("/clase1", response_class=HTMLResponse)
async def clase1(request: Request):
    return templates.TemplateResponse(request, "clase1.html")
```
Sirve el contenido teorico de cada clase. No toca la base de datos: son paginas HTML generadas previamente por `convertir_md.py`. Al estar dentro del prefijo `/clases` (definido en `main.py`), las rutas finales son `GET /clases/clase0` y `GET /clases/clase1`.

**Archivo: `routers/ejercicios.py`** — 60 lineas
```python
from services.clase0_ejercicios import ejercicios_clase0
from services.clase1_ejercicios import ejercicios_clase1

@router.get("/clase0", response_class=HTMLResponse)
async def ejercicios_c0(request: Request):
    return templates.TemplateResponse(request, "ejercicios.html", {
        "clase_num": 0, "clase_titulo": "Consultas",
        "ejercicios": ejercicios_clase0(),
    })
```
Cuatro endpoints para mostrar ejercicios y respuestas de cada clase. El router llama a las funciones de la **capa de servicios** (`ejercicios_clase0()`, `ejercicios_clase1()`) para obtener los datos, y los pasa a la plantilla. Esto es la separacion en accion: el router no sabe como se generan los ejercicios, solo los recibe y los renderiza.

**Archivo: `routers/consola.py`** — 75 lineas (el endpoint mas complejo)
```python
from sqlalchemy import text

@router.post("/consulta", response_class=HTMLResponse)
async def ejecutar_consulta_usuario(
    request: Request,
    db: AsyncSession = Depends(get_db),       # ← Capa 3 inyectada
    sql: str = Form(""),
    _rate: None = Depends(limitar_consulta),  # ← Capa 2 inyectada
):
    consulta = validar_consulta(sql)           # ← Capa 2
    async with db.begin() as tx:
        await db.execute(text("SET TRANSACTION READ ONLY"))
        result = await db.execute(text(consulta))
        filas = result.mappings().all()
        resultado = [dict(f) for f in filas[:50]]
        await tx.rollback()
```
Este endpoint recibe SQL desde un `<textarea>` via POST, lo valida (servicio `validador_sql.py`), lo ejecuta contra PostgreSQL (capa de datos `get_db()`), y renderiza los resultados en una tabla HTML. Si hay error, lo captura y lo muestra al usuario. El rate limiter corre como **dependencia de FastAPI** que se evalua antes de ejecutar el handler.

**Archivo: `main.py`** — 58 lineas (aplicacion principal)
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    tarea = asyncio.create_task(mantener_base_de_datos_viva())  # ← Capa 2
    yield
    tarea.cancel()

app = FastAPI(title="CS50 SQL — Adaptacion a PostgreSQL", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(clases.router, prefix="/clases")
app.include_router(ejercicios.router, prefix="/ejercicios")
app.include_router(consola.router)
```
Registra los routers con sus prefijos, monta los archivos estaticos, define el `lifespan` para la tarea de keep-alive, y expone dos rutas propias: `GET /` (pagina de inicio) y `GET /health` (healthcheck que ejecuta `SELECT 1` para verificar conectividad con la BD). Tambien define un manejador global `@app.exception_handler(500)` que renderiza `500.html`.

### Capa 2 — Servicios (Logica de negocio)

Contiene la **inteligencia del sistema**: validaciones, estructuras de datos, reglas de negocio y ejercicios. Ningun modulo aqui sabe de HTTP ni de HTML.

**Archivo: `services/ejercicios.py`** — El modelo de datos central
```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Ejercicio:
    id: str                          # "c0_01", "c1_15"
    numero: int                      # orden de presentacion
    titulo: str                      # "Autores por editorial"
    enunciado: str                   # texto descriptivo del problema
    dificultad: str                  # "basico" | "intermedio" | "avanzado"
    sql: str                         # la consulta SQL solucion
    params: dict[str, Any] = field(default_factory=dict)
```
Un **dataclass** puro: no tiene logica, es una simple bolsa de datos que define la *forma* de un ejercicio. Todos los modulos de ejercicios instancian esta clase. Los templates Jinja2 reciben listas de `Ejercicio` y acceden a sus atributos (`e.numero`, `e.titulo`, `e.dificultad`, `e.sql`...). Usar un dataclass en vez de un diccionario da autocompletado en el editor y evidencia errores de tipeo en tiempo de desarrollo.

**Archivos: `services/clase0_ejercicios.py` y `services/clase1_ejercicios.py`**

Cada uno exporta una funcion que devuelve una lista de objetos `Ejercicio`:
- `ejercicios_clase0()` → 35 ejercicios sobre SELECT, WHERE, LIKE, ORDER BY, funciones de agregacion (COUNT, AVG, MIN, MAX, SUM), GROUP BY, HAVING.
- `ejercicios_clase1()` → 32 ejercicios sobre INNER JOIN, LEFT/RIGHT/FULL JOIN, NATURAL JOIN, subconsultas, INTERSECT, UNION, EXCEPT, GROUP BY + HAVING.

Cada ejercicio incluye su **consulta SQL solucion** (en sintaxis PostgreSQL). Estos archivos son puramente declarativos: no tienen logica compleja, solo construyen y devuelven listas.

**Archivo: `services/validador_sql.py`** — Seguridad de consultas
```python
PELIGROSAS = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
              "TRUNCATE", "COPY", "GRANT", "REVOKE", ...}
PERMITIDAS = {"SELECT", "WITH", "EXPLAIN"}

def validar_consulta(sql: str) -> str:
    limpio = sql.strip()
    if ";" in limpio:
        raise ValueError("No se permiten multiples sentencias (;)")
    sin_literales = _eliminar_literales(limpio)   # quita strings y comentarios
    primera = sin_literales.split(None, 1)[0].upper()
    if primera not in PERMITIDAS:
        raise ValueError(...)
    palabras = set(_RE_PALABRAS.findall(sin_literales.upper()))
    prohibidas = palabras & PELIGROSAS
    if prohibidas:
        raise ValueError(...)
    return limpio
```
Antes de enviar SQL a PostgreSQL, este validador:
1. Rechaza multiples sentencias (detecta `;`).
2. Elimina comentarios SQL (`--`, `/* */`) y literales de string (`'...'`, `E'...'`, `$$...$$`) para que no se usen como evasion.
3. Verifica que la primera palabra sea SELECT, WITH o EXPLAIN.
4. Busca palabras prohibidas en lo que queda del SQL.

Si todo pasa, devuelve la consulta original limpia. Si algo falla, lanza `ValueError` con un mensaje descriptivo.

**Archivo: `services/rate_limit.py`** — Proteccion contra abuso
```python
class RateLimiter:
    def __init__(self, peticiones: int = 10, ventana: int = 60):
        self.peticiones = peticiones
        self.ventana = ventana
        self._registros: dict[str, list[float]] = defaultdict(list)

    def __call__(self, request: Request):
        ip = request.client.host
        ahora = time.time()
        corte = ahora - self.ventana
        self._registros[ip] = [t for t in self._registros[ip] if t > corte]
        if len(self._registros[ip]) >= self.peticiones:
            raise HTTPException(status_code=429, ...)
        self._registros[ip].append(ahora)

limitar_consulta = RateLimiter(peticiones=10, ventana=60)
```
Implementa **sliding window** en memoria. Cada IP tiene una lista de timestamps. En cada peticion se descartan los timestamps fuera de la ventana (60 segundos) y se cuenta cuantos quedan. Si superan 10, se devuelve HTTP 429. La clase implementa `__call__`, lo que permite usarla como **dependencia inyectable**: `Depends(limitar_consulta)`. FastAPI la ejecuta automaticamente antes del handler.

**Archivo: `services/keep_alive.py`** — Mantener viva la BD en Neon
```python
async def mantener_base_de_datos_viva(intervalo: int = 240):
    while True:
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(text("SELECT 1"))
        except Exception:
            logger.warning("Fallo el ping a la base de datos", exc_info=True)
        await asyncio.sleep(intervalo)
```
Neon suspende las bases de datos inactivas en su capa gratuita, y el "cold start" puede demorar varios segundos. Esta tarea asincrona ejecuta `SELECT 1` cada 4 minutos para mantener la conexion caliente. Se lanza en el `lifespan` de FastAPI (`main.py`) como tarea de fondo (`asyncio.create_task`), y se cancela al apagar el servidor.

### Capa 3 — Datos (Acceso a base de datos)

**Archivo: `database.py`** — Unico punto de contacto con PostgreSQL
```python
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://profesor:profesor@localhost/sql_teach"
)

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=5, max_overflow=10)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

Desglose de cada linea:

1. **`create_async_engine(DATABASE_URL, ...)`** — Crea el motor asincrono que gestiona el pool de conexiones a PostgreSQL. `pool_size=5` significa 5 conexiones permanentes mantenidas abiertas. `max_overflow=10` permite hasta 10 conexiones adicionales temporales en picos de trafico. `echo=False` evita que SQLAlchemy imprima cada consulta SQL en consola.
2. **`async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)`** — Crea una fabrica de sesiones asincronas. Cada sesion es una transaccion ligera contra la BD. `expire_on_commit=False` evita que SQLAlchemy invalide objetos al hacer commit (importante en contexto web donde la sesion se descarta al terminar el request).
3. **`get_db()`** — Generador asincrono usado como **dependencia de FastAPI**. FastAPI llama a `get_db()` al inicio del request, obtiene una sesion, la inyecta en el parametro `db`, y automaticamente cierra la sesion al terminar el request (gracias al `async with`). Este patron garantiza que nunca se filtren conexiones.

### Flujo completo de una peticion

Veamos paso a paso que ocurre cuando un usuario escribe `SELECT * FROM libros LIMIT 5;` en la consola SQL y presiona Ctrl+Enter:

```
1. NAVEGADOR
   └─ POST /consulta  (Content-Type: application/x-www-form-urlencoded)
      Body: sql=SELECT * FROM libros LIMIT 5;

2. FASTAPI recibe la peticion
   └─ Resuelve la dependencia limitar_consulta (RateLimiter)
      └─ ¿Esta IP ha hecho +10 consultas en el ultimo minuto?
         ├─ SI  → HTTP 429 "Demasiadas consultas. Espera unos segundos."
         └─ NO  → Continuar

3. └─ Resuelve la dependencia get_db()
      └─ Crea una AsyncSession desde el pool de conexiones

4. HANDLER: ejecutar_consulta_usuario()
   ├─ validar_consulta(sql)                          ← Capa 2: validador
   │  ├─ Elimina comentarios y literales de string
   │  ├─ Verifica que la primera palabra sea SELECT, WITH o EXPLAIN
   │  └─ Busca palabras prohibidas (INSERT, DROP, ...)
   │     └─ Si encuentra alguna → ValueError → error mostrado al usuario
   ├─ db.begin()                                     ← Capa 3: inicia transaccion
   ├─ db.execute(text("SET TRANSACTION READ ONLY"))  ← Capa 3: modo solo lectura
   ├─ db.execute(text(consulta))                     ← Capa 3: ejecuta la consulta
   │  └─ PostgreSQL procesa SELECT * FROM libros LIMIT 5
   │     └─ Devuelve 5 filas con columnas: isbn, titulo, ano, paginas, editorial_id
   ├─ result.mappings().all()                        ← Convierte filas a dicts
   ├─ [:50]                                          ← Limita a 50 filas maximo
   └─ tx.rollback()                                  ← Cierra la transaccion sin cambios

5. TEMPLATE: consola.html recibe {"resultado": [...], "error": None, "sql_anterior": "SELECT..."}
   └─ Jinja2 renderiza una tabla HTML con los resultados
      └─ Itera sobre cada fila y cada columna
         └─ <table><thead><tr><th>isbn</th><th>titulo</th>...</tr></thead>...</table>

6. NAVEGADOR
   └─ Muestra la tabla con las 5 filas debajo del textarea
```

Cada capa tiene una responsabilidad clara y acotada. Si manana quisieras cambiar PostgreSQL por MySQL, solo modificarias `database.py`. Si quisieras cambiar el motor de plantillas, solo tocarias `templating.py` y los templates. Si quisieras anadir Google OAuth para la consola, agregarias un servicio en `services/` y lo inyectarias en el router.

---

## SQL crudo con `text()` de SQLAlchemy

### Que es `sqlalchemy.text()`

`text()` es una funcion de SQLAlchemy que permite escribir **consultas SQL como strings literales**, sin pasar por el ORM (Object-Relational Mapper). A diferencia del ORM tradicional donde defines modelos como clases Python (`class Libro(Base): ...`), `text()` te deja escribir SQL directamente:

```python
from sqlalchemy import text

# Con text(): escribes SQL crudo, tu controlas cada palabra
consulta = text("SELECT titulo, ano FROM libros WHERE paginas > :min_paginas")
resultado = await db.execute(consulta, {"min_paginas": 500})

# Sin text() (ORM tradicional): SQLAlchemy genera el SQL por ti
# resultado = await db.execute(select(Libro.titulo, Libro.ano).where(Libro.paginas > 500))
```

**Ventajas de usar `text()` (el enfoque de este proyecto):**

| Aspecto | `text()` (SQL crudo) | ORM tradicional |
|---|---|---|
| Control | Tu escribes cada palabra del SQL | SQLAlchemy genera el SQL |
| Curva de aprendizaje | Solo necesitas saber SQL | Necesitas aprender la API del ORM |
| Rendimiento | Igual que el SQL que escribiste | Puede generar consultas ineficientes si no conoces bien el ORM |
| Portabilidad | Depende de tu dialecto SQL | SQLAlchemy traduce entre dialectos |
| Seguridad | **Parametros bind** previenen inyeccion SQL | Previene inyeccion por diseno |
| Uso tipico | Consultas complejas, reportes, migraciones | CRUD simple, relaciones entre objetos |

Este proyecto usa `text()` porque el **objetivo es ensenar SQL**, no un ORM. Cada consulta de ejemplo en las clases, cada solucion de ejercicio, y cada consulta que el usuario escribe en la consola se ejecuta exactamente como fue escrita. Esto hace que la herramienta sea fiel al proposito educativo: lo que el estudiante escribe es lo que PostgreSQL ejecuta.

### Como se usa en este proyecto

**En el healthcheck** (`main.py:48`):
```python
@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
```
La consulta mas simple posible. `SELECT 1` no toca ninguna tabla, solo verifica que la conexion esta viva. Si PostgreSQL responde, el servidor esta sano.

**En la consola SQL** (`routers/consola.py:51-56`):
```python
async with db.begin() as tx:
    await db.execute(text("SET TRANSACTION READ ONLY"))
    result = await db.execute(text(consulta))
    if result.returns_rows:
        filas = result.mappings().all()
        resultado = [dict(f) for f in filas[:50]]
```
Aqui la consulta viene directamente del usuario (string desde un `<textarea>`). El flujo es:
1. La consulta ya fue validada por `validador_sql.py`.
2. Se abre una transaccion explicita con `db.begin()`.
3. Se configura como `READ ONLY` a nivel de PostgreSQL (segunda capa de defensa).
4. Se ejecuta con `text(consulta)`.
5. `result.returns_rows` es `True` si la consulta devuelve filas (SELECT) o `False` si no (SET, EXPLAIN sin datos, etc.).
6. `result.mappings().all()` convierte las filas a una lista de diccionarios tipo `RowMapping`.
7. `[dict(f) for f in filas[:50]]` convierte cada `RowMapping` a un `dict` nativo de Python y limita a 50 filas para no sobrecargar el navegador.

**En el keep-alive** (`services/keep_alive.py:15`):
```python
async with AsyncSessionLocal() as db:
    await db.execute(text("SELECT 1"))
```
Misma consulta, pero con su propia sesion independiente. No usa `get_db()` porque no esta en el contexto de un request HTTP.

### Transacciones manuales con `begin()` y `rollback()`

El endpoint `POST /consulta` usa un patron importante:

```python
async with db.begin() as tx:
    await db.execute(text("SET TRANSACTION READ ONLY"))
    result = await db.execute(text(consulta))
    # ... procesar resultados ...
    await tx.rollback()   # ← Siempre rollback, nunca commit
```

**Por que `rollback()` en vez de `commit()`?** Porque aunque la consulta sea de solo lectura, PostgreSQL aun registra la transaccion. Hacer `rollback()` explicito:
- Libera los recursos de la transaccion inmediatamente.
- Garantiza que ningun dato se modifique (defensa en profundidad).
- Es inocuo para SELECT: los datos leidos ya estan en memoria.

Si no hicieramos `rollback()`, el `async with db.begin() as tx:` hara `commit()` automaticamente al salir del bloque. Aunque con `READ ONLY` no habria cambios que confirmar, el rollback explicito hace explicita la intencion: "esto es solo lectura, no toques nada".

### Procesamiento de resultados con `mappings()`

Cuando ejecutas `SELECT * FROM libros`, SQLAlchemy devuelve un objeto `CursorResult`. Tienes varias formas de leer las filas:

```python
result = await db.execute(text("SELECT isbn, titulo FROM libros LIMIT 3"))

# Opcion 1: mappings() → dict-like (usado en este proyecto)
filas = result.mappings().all()
# [{'isbn': '978-0-099-54094-6', 'titulo': 'Moon Tiger'}, ...]

# Opcion 2: all() → tuplas (Row)
filas = result.all()
# [('978-0-099-54094-6', 'Moon Tiger'), ...]

# Opcion 3: fetchone() → una sola fila
fila = result.fetchone()

# Opcion 4: scalars() → primera columna de cada fila
isbns = result.scalars().all()
# ['978-0-099-54094-6', '978-0-571-23558-0', ...]
```

El proyecto usa `mappings()` porque devuelve filas como estructuras similares a `dict`, lo que permite pasarlas directamente a Jinja2 para iterar con `{% for columna, valor in fila.items() %}`.

### El patron `get_db()` — dependencia asincrona de FastAPI

La funcion `get_db()` en `database.py` es uno de los patrones mas elegantes de FastAPI:

```python
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

Cuando FastAPI ve `db: AsyncSession = Depends(get_db)` en un handler:
1. Llama a `get_db()`, que entra al `async with` y crea una sesion.
2. `yield session` pausa la funcion y entrega la sesion al handler.
3. El handler usa `db` para ejecutar consultas.
4. Cuando el handler termina, FastAPI reanuda `get_db()` justo despues del `yield`.
5. El `async with` cierra la sesion automaticamente (la devuelve al pool).

Esto garantiza que **cada request tiene su propia sesion** y que **las sesiones siempre se cierran**, incluso si el handler lanza una excepcion. No hay que escribir `try/finally` manualmente: FastAPI y el context manager de SQLAlchemy lo manejan.

---

## Seguridad

La consola SQL permite a cualquier usuario ejecutar consultas contra la base de datos real. Esto es inherentemente peligroso. El proyecto implementa **defensa en profundidad** (defense in depth) con tres capas independientes:

### Validador de SQL

`services/validador_sql.py` es la primera linea de defensa. Antes de que la consulta llegue a PostgreSQL, el validador:

1. **Rechaza multiples sentencias**: busca `;` en el string. Asi se bloquean ataques como `SELECT 1; DROP TABLE libros;`.
2. **Elimina literales y comentarios antes de analizar**: para que `SELECT * FROM libros WHERE titulo = 'DROP TABLE'` no se bloquee falsamente. Elimina strings entre comillas (`'...'`, `E'...'`, `$$...$$`) y comentarios (`--`, `/* */`).
3. **Verifica la primera palabra**: debe ser SELECT, WITH o EXPLAIN.
4. **Busca palabras prohibidas**: tras eliminar literales, busca comandos como INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, COPY, GRANT, REVOKE, etc. Si encuentra alguna, rechaza la consulta.

Si el validador falla, el usuario ve un mensaje de error en rojo en la consola. La consulta nunca llega a PostgreSQL.

### Rate limiting por IP

`services/rate_limit.py` limita a **10 consultas por minuto por direccion IP**. Esto previene:
- Fuerza bruta tratando de evadir el validador.
- Denegacion de servicio (DoS) saturando la base de datos con consultas pesadas.
- Scraping masivo de datos.

El rate limiter usa el algoritmo **sliding window**: cada IP tiene una lista de timestamps. Cuando llega una peticion, se descartan los timestamps con mas de 60 segundos de antiguedad. Si quedan 10 o mas, se devuelve HTTP 429 (Too Many Requests). El usuario ve el error en la interfaz.

La clase `RateLimiter` implementa `__call__(self, request: Request)`, lo que permite usarla como **dependencia de FastAPI**:
```python
@router.post("/consulta", response_class=HTMLResponse)
async def ejecutar_consulta_usuario(
    ...
    _rate: None = Depends(limitar_consulta),  # ← se evalua antes del handler
):
```
FastAPI llama a `limitar_consulta(request)` antes de ejecutar el handler. Si lanza `HTTPException`, el handler nunca se ejecuta.

### Transacciones READ ONLY en PostgreSQL

Incluso si el validador SQL y el rate limiter fallaran, hay una tercera capa a nivel de base de datos:

```python
await db.execute(text("SET TRANSACTION READ ONLY"))
```

Esta instruccion le dice a PostgreSQL que la transaccion actual es de solo lectura. Si alguien lograra colar un INSERT, UPDATE o DELETE, PostgreSQL lo rechazaria con un error. Esta es la capa mas fuerte porque la aplica el propio motor de base de datos.

### Keep-alive para Neon (PostgreSQL serverless)

`services/keep_alive.py` resuelve un problema operacional, no de seguridad: Neon suspende las bases de datos inactivas en su capa gratuita tras ~5 minutos sin actividad. El "cold start" (despertar la BD) puede demorar varios segundos, dando una mala experiencia al usuario.

La solucion: una tarea asincrona en background que ejecuta `SELECT 1` cada 4 minutos mientras el servidor esta vivo. Esto mantiene la base de datos "caliente" y las consultas responden instantaneamente. La tarea se lanza en el `lifespan` de FastAPI:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    tarea = asyncio.create_task(mantener_base_de_datos_viva())
    yield            # ← el servidor corre aqui
    tarea.cancel()   # ← al apagar, se cancela la tarea
```

---

## Sistema de plantillas Jinja2

El proyecto usa **Jinja2** a traves de `fastapi.templating.Jinja2Templates`. La instancia se crea una sola vez en `templating.py` y se comparte entre todos los modulos para evitar duplicacion:

```python
# templating.py
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")
```

Todas las plantillas heredan de `templates/base.html` usando `{% extends "base.html" %}`. Esto significa que el `<head>`, la barra de navegacion, Mermaid.js y la estructura del `<body>` se definen una sola vez.

```html
<!-- base.html (simplificado) -->
<!doctype html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <title>{% block title %}CS50 SQL{% endblock %}</title>
    <link rel="stylesheet" href="/static/estilos.css" />
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav>...</nav>
    <div class="container">{% block content %}{% endblock %}</div>
    {% block extra_js %}{% endblock %}
    <script src="...mermaid.min.js"></script>
</body>
</html>
```

Cada pagina define los bloques que necesita:
- `clase0.html` / `clase1.html`: definen `title` y `content` con el HTML de la clase.
- `consola.html`: define `title`, `content`, `extra_css` (ancho extendido) y `extra_js` (atajo Ctrl+Enter).
- `ejercicios.html`: define `title` y `content` iterando sobre `{% for e in ejercicios %}`.
- `respuestas.html`: define `title` y `content` mostrando `{{ e.sql }}` en bloques `<pre>`.

Los templates reciben datos desde los routers via `TemplateResponse(request, "plantilla.html", {"clave": valor})`. Jinja2 renderiza el HTML combinando la plantilla base con los bloques definidos por cada pagina.

`templates/500.html` es la unica plantilla que no extiende `base.html`: es una pagina de error minimalista servida por `@app.exception_handler(500)`.

---

## Conversion de Markdown a HTML

El contenido teorico de las clases existe como archivos **Markdown** (`.md`) fuera del proyecto. El script `convertir_md.py` los transforma en plantillas Jinja2 listas para servir.

El pipeline de conversion hace 5 transformaciones:

1. **Reescribe rutas de imagenes**: `![](images/p6.jpg)` → `![](/static/images/p6.jpg)` para que funcionen con el montaje de archivos estaticos de FastAPI.
2. **Convierte Markdown a HTML** con `markdown_it` (soporte CommonMark + tablas).
3. **Envuelve tablas** en `<div class="table-wrapper">` para permitir scroll horizontal en pantallas chicas (las tablas de datos del Booker Prize son anchas).
4. **Convierte bloques Mermaid**: los bloques de codigo marcados como ` ```mermaid ` se transforman en `<div class="mermaid">` para que la libreria Mermaid.js (cargada en `base.html`) los renderice como diagramas ER en el navegador.
5. **Envuelve el HTML** en una plantilla Jinja2 que extiende `base.html`.

El script se ejecuta manualmente cuando el contenido Markdown cambia:
```bash
uv run python convertir_md.py
```

Esto genera `templates/clase0.html` y `templates/clase1.html`.

---

## Ejercicios y sistema de auto-evaluacion

Cada clase tiene su propio conjunto de ejercicios, definidos en la capa de servicios:

- **Clase 0 (Consultas):** 35 ejercicios en `services/clase0_ejercicios.py`
  - Basicos (1-7, 26-29): SELECT *, columnas, LIMIT, WHERE =/!=/<>/NOT, LIKE %/\_, OR
  - Intermedios (8-15, 30-32): ILIKE, BETWEEN, IS NULL, AND/OR con parentesis, ORDER BY mixto
  - Avanzados (16-25, 33-35): AVG, COUNT DISTINCT, MAX, MIN, SUM, subconsultas, GROUP BY, HAVING

- **Clase 1 (Relaciones):** 32 ejercicios en `services/clase1_ejercicios.py`
  - Basicos (1-7, 23-24): INNER JOIN, LEFT JOIN, NATURAL JOIN, subconsultas simples
  - Intermedios (8-15, 25-28): IN con subconsulta, INTERSECT, UNION, EXCEPT, FULL JOIN
  - Avanzados (16-22, 29-32): Subconsultas anidadas de 3 niveles, JOIN + GROUP BY + LIMIT, HAVING COUNT >= N

Cada ejercicio se define como una instancia del dataclass `Ejercicio`:

```python
Ejercicio(
    id="c0_01",
    numero=1,
    titulo="Primera consulta",
    enunciado="Escribe una consulta para seleccionar todos los libros de la tabla `libros`.",
    dificultad="basico",
    sql="SELECT * FROM libros;"
)
```

Las paginas de ejercicios (`/ejercicios/clase0`, `/ejercicios/clase1`) muestran cada ejercicio en una card con:
- Numero y titulo.
- Badge de dificultad (verde = basico, amarillo = intermedio, rojo = avanzado).
- Enunciado.
- Borde izquierdo coloreado segun dificultad.

Las hojas de respuestas (`/ejercicios/clase0/respuestas`, `/ejercicios/clase1/respuestas`) muestran el enunciado seguido de la **consulta SQL solucion** en un bloque `<pre>`. Incluyen una advertencia amarilla animando al estudiante a intentar resolver el ejercicio por su cuenta antes de mirar la respuesta.

---

## Patrones de diseno usados

| Patron | Donde se usa | Que resuelve |
|---|---|---|
| **Arquitectura de 3 capas** | `routers/` → `services/` → `database.py` | Separacion de responsabilidades: HTTP, logica y persistencia no se mezclan |
| **Dependency Injection** | `Depends(get_db)`, `Depends(limitar_consulta)` | FastAPI inyecta dependencias en los handlers. Facilita testing y desacoplamiento |
| **Singleton** | `templating.py` (instancia unica de `Jinja2Templates`), `rate_limit.py` (`limitar_consulta`) | Una sola instancia compartida por toda la aplicacion |
| **Template Method** | `templates/base.html` con `{% block %}` | Define un esqueleto comun y deja que cada pagina rellene los bloques |
| **Strategy** | `validador_sql.py` (regex precompilados como estrategias de eliminacion) | Diferentes tipos de literales SQL se eliminan con diferentes estrategias regex |
| **Observer (simplificado)** | `lifespan` de FastAPI `@asynccontextmanager` | Reacciona a eventos de inicio/apagado del servidor |
| **Dataclass (DTO)** | `services/ejercicios.py` | Transporta datos entre capas sin logica acoplada |
| **Generator (yield)** | `get_db()` | Manejo automatico de recursos: la sesion se crea y se destruye sin intervencion manual |
| **Sliding Window** | `rate_limit.py` | Control de tasa con ventana deslizante en memoria |

---

## Estructura completa del proyecto

```
consultas_sql/
│
├── main.py                      # Punto de entrada: app FastAPI, lifespan, rutas / y /health
├── database.py                  # Capa 3: conexion async a PostgreSQL (SQLAlchemy + asyncpg)
├── templating.py                # Instancia unica compartida de Jinja2Templates
├── convertir_md.py              # Script offline: Markdown → plantillas Jinja2 (clase0/1.html)
├── pyproject.toml               # Configuracion del proyecto + dependencias (uv / pip)
├── requirements.txt             # Dependencias para pip / despliegue en Vercel
├── datos.sql                    # Dump completo de la BD (esquema + datos de 10 tablas)
├── README.md                    # Este documento
├── CONTRIBUTING.md              # Guia de contribucion
├── .env                         # Variables de entorno reales (no incluido en git)
├── .env-sample                  # Plantilla para .env
├── .gitignore                   # Archivos ignorados por git
│
├── routers/                     # CAPA 1 — Presentacion / Controladores
│   ├── __init__.py              # Marca el directorio como paquete Python
│   ├── clases.py                # GET /clases/clase0, GET /clases/clase1
│   ├── ejercicios.py            # GET /ejercicios/clase{0,1}, GET /ejercicios/clase{0,1}/respuestas
│   └── consola.py               # GET /consola, POST /consulta
│
├── services/                    # CAPA 2 — Logica de negocio
│   ├── ejercicios.py            # Dataclass Ejercicio (modelo de datos)
│   ├── clase0_ejercicios.py     # 35 ejercicios de la Clase 0 (Consultas)
│   ├── clase1_ejercicios.py     # 32 ejercicios de la Clase 1 (Relaciones)
│   ├── validador_sql.py         # Validador de seguridad: solo SELECT / WITH / EXPLAIN
│   ├── rate_limit.py            # Rate limiter: max 10 consultas/min por IP
│   └── keep_alive.py            # Ping a PostgreSQL cada 4 min (evita suspension en Neon)
│
├── templates/                   # Vistas Jinja2
│   ├── base.html                # Layout comun: nav, CSS, Mermaid.js, bloques extensibles
│   ├── index.html               # Pagina de inicio con descripcion y esquema de la BD
│   ├── clase0.html              # Contenido Clase 0: Consultas (generado por convertir_md.py)
│   ├── clase1.html              # Contenido Clase 1: Relaciones (generado por convertir_md.py)
│   ├── ejercicios.html          # Listado de ejercicios con cards y badges de dificultad
│   ├── respuestas.html          # Hoja de respuestas con consultas SQL solucion
│   ├── consola.html             # Consola SQL interactiva (textarea + tabla de resultados)
│   └── 500.html                 # Pagina de error 500
│
└── static/                      # Archivos estaticos servidos por FastAPI
    ├── estilos.css              # CSS unificado (~850 lineas): modo oscuro, responsive
    └── images/                  # Imagenes del curso original (p6.jpg, p8.jpg, etc.)
```

---

## Creditos

El contenido original pertenece al curso **CS50's Introduction to Databases with SQL** de Harvard University, disponible en [cs50.harvard.edu/sql](https://cs50.harvard.edu/sql/).

---

## Licencia

MIT — puedes usar, copiar, modificar y distribuir este software libremente para cualquier proposito, incluyendo uso comercial, siempre que mantengas el aviso de copyright.

```
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
