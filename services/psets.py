"""Problem Sets de CS50 SQL (psets/1) — traducidos al español paisa.

Cada pset (DESE, Moneyball, Packages, Please) se carga en su propio esquema
de PostgreSQL (dese, moneyball, packages) y los enunciados se tradujeron al
español para que jóvenes de Medellín los entiendan con claridad. Los links
de descarga apuntan a la página original de Harvard.

Los SQL esperados se adaptaron a PostgreSQL (mismas consultas que la
solución oficial, ajustando sintaxis donde hace falta, p. ej. ROUND de
doble argumento, AS con comillas para alias con espacios).
"""

from __future__ import annotations

from services.ejercicios import Ejercicio
from services.psets_dese import ejercicios_dese
from services.psets_moneyball import ejercicios_moneyball
from services.psets_packages import ejercicios_packages


def todos_los_psets() -> dict[str, list[Ejercicio]]:
    """Devuelve un dict {slug_pset: [Ejercicio, ...]}."""
    return {
        "dese": ejercicios_dese(),
        "moneyball": ejercicios_moneyball(),
        "packages": ejercicios_packages(),
    }


def pset_por_slug(slug: str) -> list[Ejercicio] | None:
    return todos_los_psets().get(slug)


def ejercicio_por_id(eid: str) -> Ejercicio | None:
    for lista in todos_los_psets().values():
        for e in lista:
            if e.id == eid:
                return e
    return None


# ── Metadata de cada pset (título, descripción, url original, url descarga) ─

PSETS_META: dict[str, dict[str, str]] = {
    "dese": {
        "slug": "dese",
        "titulo": "DESE — Educación en Massachusetts",
        "descripcion": (
            "Asumí el rol de analista de datos del Departamento de Educación "
            "de Massachusetts. Resolvé preguntas sobre escuelas, distritos, "
            "graduaciones y gastos usando JOIN, GROUP BY y subconsultas."
        ),
        "url_original": "https://cs50.harvard.edu/sql/psets/1/dese/",
        "url_descarga": "https://cdn.cs50.net/sql/2024/x/psets/1/dese.zip",
        "esquema": "dese",
        "bd_sqlite": "dese.db",
        "repo_archivos": "13 archivos .sql",
        "contexto": (
            "Trabajás como analista de datos para el Estado de Massachusetts, en "
            "el Departamento de Educación Primaria y Secundaria (DESE, por sus "
            "siglas en inglés). DESE vigila el sistema de escuelas públicas del "
            "estado. Su deber es asegurar que todo chamito tenga una educación "
            "de calidad: con docentes con experiencia, abundantes recursos y que, "
            "al graduarse, cumplan todos los requisitos del estado."
        ),
    },
    "moneyball": {
        "slug": "moneyball",
        "titulo": "Moneyball — Béisbol y estadísticas",
        "descripcion": (
            "Sos el analista de los Oakland Athletics en 2001. Con poco "
            "presupuesto, encontrá el valor escondido en jugadores que otros "
            "equipos no ven. JOIN, agregaciones y subconsultas anidadas."
        ),
        "url_original": "https://cs50.harvard.edu/sql/psets/1/moneyball/",
        "url_descarga": "https://cdn.cs50.net/sql/2024/x/psets/1/moneyball.zip",
        "esquema": "moneyball",
        "bd_sqlite": "moneyball.db",
        "repo_archivos": "12 archivos .sql",
        "contexto": (
            "Estamos en 2001. Te contrataron para sacarle el jugo al reducido "
            "presupuesto de jugadores de los Oakland Athletics (\"los A's\"). "
            "Cada año los equipos contratan peloteros nuevos. Lástima que andás "
            "escrito de estrellas… y de plata. Pero con un poco de SQL y algo de "
            "suerte, ¿quién dice que no podés armar un equipo que rompa los "
            "esquemas? Te toca encontrarle el valor a jugadores que otros no ven."
        ),
    },
    "packages": {
        "slug": "packages",
        "titulo": "Packages, Please — Paquetes perdidos",
        "descripcion": (
            "Sos el cartero de Boston. Tres paquetes se perdieron. Con "
            "subconsultas y JOIN encontrá dónde están, qué tienen adentro y "
            "quién los tiene. Tres misterios que resolver."
        ),
        "url_original": "https://cs50.harvard.edu/sql/psets/1/packages/",
        "url_descarga": "https://cdn.cs50.net/sql/2024/x/psets/1/packages.zip",
        "esquema": "packages",
        "bd_sqlite": "packages.db",
        "repo_archivos": "log.sql + answers.txt",
        "contexto": (
            "Sos cartero (quien reparte el correo) de la ciudad de Boston. "
            "Casi todos los paquetes llegan a su destino. Pero de vez en cuando "
            "te cae un misterio: ¡un paquete perdido! Por cada cliente que "
            "llega a reportar un paquete perdido, tenés que descubrir: "
            "dónde está ahora mismo (la dirección o locación), qué tipo de "
            "dirección es (residencial, de negocio, etc.) y qué trae el paquete. "
            "Lo único que sabés es lo que el cliente te cuenta. Para resolver "
            "cada misterio tenés que usar la base de datos del servicio de "
            "correo, `packages.db`, con la info del tránsito de paquetes por "
            "la ciudad."
        ),
    },
}