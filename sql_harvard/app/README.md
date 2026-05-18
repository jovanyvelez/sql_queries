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
| Backend | Python 3.13 + FastAPI |
| Base de datos | PostgreSQL (Neon) |
| ORM / driver | SQLAlchemy 2.0 + asyncpg |
| CSS | Un solo archivo, modo oscuro |
| Diagramas | Mermaid.js |

## Ejecutar localmente

```bash
cd app
uv run fastapi dev main.py
```

La aplicacion se sirve en `http://localhost:8000`.

### Variables de entorno

Copiar `.env` (no incluido en el repositorio) con:

```
DATABASE_URL=postgresql+asyncpg://usuario:password@host/basedatos?ssl=require
```

Por defecto usa `localhost` con usuario `profesor` y base `sql_teach`.

## Estructura

```
app/
├── main.py                 # punto de entrada, lifespan, ruta /
├── templating.py            # Jinja2Templates compartido
├── database.py              # conexion a PostgreSQL
├── routers/                 # rutas agrupadas por funcion
│   ├── clases.py            # /clase0, /clase1
│   ├── ejercicios.py        # /ejercicios/clase{0,1}, /respuestas
│   └── consola.py           # /consola, POST /consulta
├── services/                # logica de negocio
│   ├── clase0_ejercicios.py # ejercicios de la clase 0
│   ├── clase1_ejercicios.py # ejercicios de la clase 1
│   ├── keep_alive.py        # ping cada 4 min (capa gratuita Neon)
│   └── validador_sql.py     # sanitizacion de consultas (solo SELECT)
├── templates/               # plantillas Jinja2
└── static/
    ├── estilos.css          # CSS unificado
    └── images/              # imagenes del curso
```

## Seguridad

La consola SQL solo permite consultas de lectura (`SELECT`, `WITH`, `EXPLAIN`). Las operaciones de escritura (`INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.) estan bloqueadas tanto a nivel de aplicacion como de base de datos (transacciones `READ ONLY`).

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
