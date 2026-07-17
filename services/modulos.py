"""Reestructuración del contenido en módulos temáticos cortos.

Cada curso (consultas, relaciones) se divide en ~6 módulos. Cada módulo agrupa
1-3 secciones <h2> del contenido original más los ejercicios relacionados.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from services.clase0_ejercicios import ejercicios_clase0
from services.clase1_ejercicios import ejercicios_clase1
from services.ejercicios import Ejercicio

CONTENT_DIR = Path(__file__).resolve().parent.parent / "templates" / "content"


@dataclass
class Modulo:
    curso: str
    slug: str
    titulo: str
    descripcion: str
    orden: int
    teoria_html: str
    ejercicios: list[Ejercicio] = field(default_factory=list)
    intro: bool = False


# ── Metadata de módulos (orden = orden de presentación) ──────────────────────

_MODULOS_META: dict[str, list[dict[str, object]]] = {
    "consultas": [
        {
            "slug": "bases-y-postgresql",
            "titulo": "Bases de datos y PostgreSQL",
            "descripcion": "Qué es una base de datos, SQL y tu primer contacto con PostgreSQL en Neon.",
            "intro": True,
        },
        {
            "slug": "select-y-limit",
            "titulo": "SELECT y LIMIT",
            "descripcion": "Tu primera consulta: elegir columnas y limitar el número de filas.",
            "intro": False,
        },
        {
            "slug": "where-y-null",
            "titulo": "WHERE y NULL",
            "descripcion": "Filtra filas con condiciones (=, !=, <>, NOT, AND, OR) y maneja valores ausentes.",
            "intro": False,
        },
        {
            "slug": "like-y-patrones",
            "titulo": "LIKE y patrones",
            "descripcion": "Búsquedas por patrón con los comodines % y _.",
            "intro": False,
        },
        {
            "slug": "rangos-y-order-by",
            "titulo": "Rangos y ORDER BY",
            "descripcion": "Operadores de comparación, BETWEEN y cómo ordenar resultados.",
            "intro": False,
        },
        {
            "slug": "funciones-de-agregacion",
            "titulo": "Funciones de agregación",
            "descripcion": "COUNT, AVG, MIN, MAX, SUM, GROUP BY y HAVING.",
            "intro": False,
        },
    ],
    "relaciones": [
        {
            "slug": "modelo-er-y-claves",
            "titulo": "Modelo ER y claves",
            "descripcion": "Diagramas entidad-relación, claves primarias y foráneas.",
            "intro": True,
        },
        {
            "slug": "subconsultas-e-in",
            "titulo": "Subconsultas e IN",
            "descripcion": "Consultas dentro de consultas y el operador IN.",
            "intro": False,
        },
        {
            "slug": "join",
            "titulo": "JOIN",
            "descripcion": "INNER, LEFT, RIGHT, FULL y NATURAL JOIN para combinar tablas.",
            "intro": False,
        },
        {
            "slug": "conjuntos",
            "titulo": "Conjuntos",
            "descripcion": "UNION, INTERSECT y EXCEPT para combinar resultados.",
            "intro": False,
        },
        {
            "slug": "grupos",
            "titulo": "Grupos (GROUP BY)",
            "descripcion": "Agregaciones por grupo con GROUP BY y HAVING.",
            "intro": False,
        },
    ],
}

# ── Mapping sección <h2> → slug de módulo ────────────────────────────────────

_SECCION_A_MODULO: dict[str, dict[str, str]] = {
    "consultas": {
        "Introduccion": "bases-y-postgresql",
        "Que es una Base de Datos?": "bases-y-postgresql",
        "SQL": "bases-y-postgresql",
        "Primeros Pasos con PostgreSQL": "bases-y-postgresql",
        "SELECT": "select-y-limit",
        "LIMIT": "select-y-limit",
        "WHERE": "where-y-null",
        "NULL": "where-y-null",
        "LIKE": "like-y-patrones",
        "Rangos": "rangos-y-order-by",
        "ORDER BY": "rangos-y-order-by",
        "Funciones de Agregacion": "funciones-de-agregacion",
        "Fin": "funciones-de-agregacion",
    },
    "relaciones": {
        "Introduccion": "modelo-er-y-claves",
        "Diagramas Entidad-Relacion": "modelo-er-y-claves",
        "Claves": "modelo-er-y-claves",
        "Subconsultas": "subconsultas-e-in",
        "IN": "subconsultas-e-in",
        "JOIN": "join",
        "Conjuntos": "conjuntos",
        "Grupos": "grupos",
        "Fin": "grupos",
    },
}

# ── Mapping ejercicio_id → slug de módulo ────────────────────────────────────

_EJERCICIOS_POR_MODULO: dict[str, dict[str, list[str]]] = {
    "consultas": {
        "select-y-limit": ["c0_01", "c0_02"],
        "where-y-null": [
            "c0_04", "c0_05", "c0_11", "c0_12", "c0_13",
            "c0_14", "c0_26", "c0_27", "c0_29",
        ],
        "like-y-patrones": ["c0_08", "c0_09", "c0_15", "c0_28"],
        "rangos-y-order-by": [
            "c0_03", "c0_06", "c0_07", "c0_10", "c0_20",
            "c0_23", "c0_24", "c0_30", "c0_31", "c0_32",
        ],
        "funciones-de-agregacion": [
            "c0_16", "c0_17", "c0_18", "c0_19", "c0_21",
            "c0_22", "c0_25", "c0_33", "c0_34", "c0_35",
        ],
    },
    "relaciones": {
        "subconsultas-e-in": ["c1_04", "c1_05", "c1_08", "c1_16", "c1_29"],
        "join": [
            "c1_01", "c1_02", "c1_03", "c1_06", "c1_07",
            "c1_20", "c1_23", "c1_24", "c1_25", "c1_26", "c1_32",
        ],
        "conjuntos": ["c1_09", "c1_10", "c1_11", "c1_15", "c1_19"],
        "grupos": [
            "c1_12", "c1_13", "c1_14", "c1_17", "c1_18",
            "c1_21", "c1_22", "c1_27", "c1_28", "c1_30", "c1_31",
        ],
    },
}

# Archivo de contenido por curso
_CURSO_CONTENT = {
    "consultas": "consultas.html",
    "relaciones": "relaciones.html",
}


def _titulo_h2(chunk: str) -> str | None:
    """Extrae el texto del <h2> que abre un chunk, sin tags internos."""
    m = re.search(r"<h2[^>]*>(.*?)</h2>", chunk, re.DOTALL)
    if not m:
        return None
    return re.sub(r"<[^>]+>", "", m.group(1)).strip()


def _split_por_h2(html: str) -> list[tuple[str, str]]:
    """Parte el HTML por secciones <h2>. Devuelve [(titulo_h2, html_seccion), ...]."""
    partes = re.split(r"(?=<h2[ >])", html)
    out: list[tuple[str, str]] = []
    for p in partes:
        p = p.strip()
        if not p:
            continue
        titulo = _titulo_h2(p)
        if titulo is None:
            continue
        out.append((titulo, p))
    return out


def _todos_ejercicios(curso: str) -> dict[str, Ejercicio]:
    if curso == "consultas":
        lista = ejercicios_clase0()
    else:
        lista = ejercicios_clase1()
    return {e.id: e for e in lista}


@lru_cache(maxsize=4)
def obtener_modulos(curso: str) -> list[Modulo]:
    """Construye (y cachea) la lista de módulos de un curso."""
    if curso not in _MODULOS_META:
        raise ValueError(f"Curso desconocido: {curso}")

    html = (CONTENT_DIR / _CURSO_CONTENT[curso]).read_text(encoding="utf-8")
    secciones = _split_por_h2(html)
    mapping_sec = _SECCION_A_MODULO[curso]
    teoria_por_modulo: dict[str, list[str]] = {m["slug"]: [] for m in _MODULOS_META[curso]}

    for titulo, chunk in secciones:
        if titulo == "Tabla de Contenidos":
            continue  # sustituida por el índice de módulos
        slug = mapping_sec.get(titulo)
        if slug is None:
            # sección no mapeada → adjuntar al último módulo conocido
            continue
        teoria_por_modulo[slug].append(chunk)

    ejercicios = _todos_ejercicios(curso)
    ej_por_mod = _EJERCICIOS_POR_MODULO[curso]

    modulos: list[Modulo] = []
    for orden, meta in enumerate(_MODULOS_META[curso]):
        slug = str(meta["slug"])
        ejerc: list[Ejercicio] = []
        for eid in ej_por_mod.get(slug, []):
            e = ejercicios.get(eid)
            if e is not None:
                e.modulo = slug
                ejerc.append(e)
        modulos.append(
            Modulo(
                curso=curso,
                slug=slug,
                titulo=str(meta["titulo"]),
                descripcion=str(meta["descripcion"]),
                orden=orden,
                teoria_html="\n".join(teoria_por_modulo[slug]),
                ejercicios=ejerc,
                intro=bool(meta["intro"]),
            )
        )
    return modulos


def obtener_modulo(curso: str, slug: str) -> Modulo | None:
    for m in obtener_modulos(curso):
        if m.slug == slug:
            return m
    return None


def curso_siguiente_modulo(curso: str, slug: str) -> Modulo | None:
    mods = obtener_modulos(curso)
    for i, m in enumerate(mods):
        if m.slug == slug and i + 1 < len(mods):
            return mods[i + 1]
    return None


def curso_anterior_modulo(curso: str, slug: str) -> Modulo | None:
    mods = obtener_modulos(curso)
    for i, m in enumerate(mods):
        if m.slug == slug and i > 0:
            return mods[i - 1]
    return None


def curso_titulo(curso: str) -> str:
    return "Consultas" if curso == "consultas" else "Relaciones"