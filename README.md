# CS50 SQL — Adaptacion a PostgreSQL (en espanol)

Aplicacion web educativa que adapta el curso **CS50's Introduction to Databases with SQL** de Harvard University al espanol, reemplazando SQLite por **PostgreSQL**.

## Proposito

Este proyecto busca hacer accesible el material del curso CS50 SQL a estudiantes hispanohablantes. Cada clase del curso original se ha traducido al espanol y sus consultas SQL se han adaptado para ejecutarse contra PostgreSQL en lugar de SQLite.

La aplicacion incluye:

- **Contenido adaptado** de las clases en formato web (markdown convertido a HTML)
- **Ejercicios interactivos** con hoja de respuestas para auto-evaluacion
- **Consola SQL** que permite ejecutar consultas contra la base de datos real
- **Modo oscuro** completo

## Tecnologias

| Componente | Tecnologia |
|---|---|
| Backend | Python >= 3.12 + FastAPI |
| Base de datos | PostgreSQL (Neon) |
| ORM / driver | SQLAlchemy 2.0 + asyncpg |
| CSS | Un solo archivo, modo oscuro |
| Diagramas | Mermaid.js |

## Base de datos

El archivo `datos.sql` contiene el esquema completo y los datos de las 10 tablas
(listo para importar en cualquier PostgreSQL >= 15):

```bash
psql -U tu_usuario -d tu_base < datos.sql
```

## Ejecutar localmente

```bash
uv run fastapi dev main.py
```

La aplicacion se sirve en `http://localhost:8000`.

### Variables de entorno

Copiar `.env-sample` a `.env` y editar con tu URL de conexion:

```
DATABASE_URL=postgresql+asyncpg://usuario:password@host/basedatos?ssl=require
```

Por defecto (si no se define `DATABASE_URL`) usa `localhost` con base `sql_teach`.

## Estructura

```
├── main.py                  # FastAPI app, lifespan, rutas / y /health
├── templating.py            # Jinja2Templates compartido
├── database.py              # conexion a PostgreSQL
├── requirements.txt         # dependencias (pip / Vercel)
├── datos.sql                # dump completo de la base de datos
├── routers/                 # rutas agrupadas con APIRouter y prefijos
│   ├── clases.py            # prefijo /clases → /clases/clase0, /clases/clase1
│   ├── ejercicios.py        # prefijo /ejercicios → /ejercicios/clase{0,1} y /respuestas
│   └── consola.py           # /consola, POST /consulta
├── services/                # logica de negocio
│   ├── ejercicios.py        # dataclass Ejercicio
│   ├── clase0_ejercicios.py # 35 ejercicios de la clase 0
│   ├── clase1_ejercicios.py # 32 ejercicios de la clase 1
│   ├── keep_alive.py        # ping cada 4 min (capa gratuita Neon)
│   ├── rate_limit.py        # limite de consultas por IP
│   └── validador_sql.py     # bloquea INSERT/UPDATE/DELETE/DROP...
├── templates/               # plantillas Jinja2
│   ├── base.html            # layout comun + nav
│   ├── index.html           # pagina de inicio
│   ├── clase0.html          # clase 0 (HTML estatico)
│   ├── clase1.html          # clase 1 (HTML estatico)
│   ├── ejercicios.html      # lista de ejercicios
│   ├── respuestas.html      # hoja de respuestas
│   ├── consola.html         # consola SQL interactiva
│   └── 500.html             # pagina de error 500
└── static/
    ├── estilos.css          # CSS unificado (modo oscuro)
    └── images/              # imagenes del curso
```

## Seguridad

- Solo consultas de lectura (`SELECT`, `WITH`, `EXPLAIN`). Las operaciones de escritura estan bloqueadas a nivel de aplicacion y base de datos (transacciones `READ ONLY`).
- Rate limiting: maximo 10 consultas por minuto por IP en la consola.
- Healthcheck: `GET /health` verifica conectividad con la base de datos.

## Creditos

El contenido original pertenece al curso **CS50's Introduction to Databases with SQL** de Harvard University, disponible en [cs50.harvard.edu/sql](https://cs50.harvard.edu/sql/).

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
