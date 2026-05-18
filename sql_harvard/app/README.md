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

Este proyecto se distribuye bajo la licencia **GNU Affero General Public License v3.0 (AGPL-3.0)**.

```
CS50 SQL — Adaptacion a PostgreSQL
Copyright (C) 2026

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
