"""Validador de ejercicios: compara el resultado del usuario con el esperado."""

import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from services.validador_sql import validar_consulta


@dataclass
class ResultadoEjercicio:
    ok: bool
    error: str | None
    columnas_esperadas: list[str]
    filas_esperadas: list[dict[str, Any]]
    columnas_obtenidas: list[str]
    filas_obtenidas: list[dict[str, Any]]
    coinciden_columnas: bool
    coinciden_filas: bool
    mensaje: str
    diagnostico: str = ""


async def probar_ejercicio(
    db: AsyncSession,
    sql_usuario: str,
    sql_esperado: str,
    orden_importa: bool,
    limite: int = 200,
    esquema: str = "public",
) -> ResultadoEjercicio:
    """Ejecuta ambas consultas en una transacción READ ONLY y compara resultados.

    - Comparación de columnas: mismas columnas (como set) en el mismo orden.
    - Comparación de filas: si orden_importa, comparación estricta en orden.
      Si no, comparación como multiconjunto (sorted) ignorando el orden de filas.
    - Se limita a `limite` filas por consulta para evitar resultados enormes.
    - `esquema`: si no es 'public', hace SET search_path TO <esquema>, public antes
      de ejecutar las consultas, para aislar las tablas de cada pset.
    """
    try:
        consulta_usuario = validar_consulta(sql_usuario)
    except Exception as e:
        return ResultadoEjercicio(
            ok=False,
            error=f"Tu consulta no es valida: {e}",
            columnas_esperadas=[],
            filas_esperadas=[],
            columnas_obtenidas=[],
            filas_obtenidas=[],
            coinciden_columnas=False,
            coinciden_filas=False,
            mensaje="invalid",
            diagnostico=_traducir_error_validacion(str(e)),
        )

    try:
        consulta_esperado = validar_consulta(sql_esperado)
    except Exception as e:
        return ResultadoEjercicio(
            ok=False,
            error=f"La consulta esperada del ejercicio es invalida: {e}",
            columnas_esperadas=[],
            filas_esperadas=[],
            columnas_obtenidas=[],
            filas_obtenidas=[],
            coinciden_columnas=False,
            coinciden_filas=False,
            mensaje="server-error",
            diagnostico="Error interno del servidor (la consulta de referencia falla).",
        )

    async with db.begin() as tx:
        await db.execute(text("SET TRANSACTION READ ONLY"))
        if esquema and esquema != "public":
            await db.execute(text(f'SET search_path TO "{esquema}", public'))

        try:
            res_usuario = await db.execute(text(consulta_usuario))
        except Exception as e:
            await tx.rollback()
            msg_tecnico = str(e)
            return ResultadoEjercicio(
                ok=False,
                error=msg_tecnico,
                columnas_esperadas=[],
                filas_esperadas=[],
                columnas_obtenidas=[],
                filas_obtenidas=[],
                coinciden_columnas=False,
                coinciden_filas=False,
                mensaje="execution-error",
                diagnostico=_traducir_error_pg(msg_tecnico),
            )

        try:
            res_esperado = await db.execute(text(consulta_esperado))
        except Exception as e:
            await tx.rollback()
            return ResultadoEjercicio(
                ok=False,
                error=f"Error al ejecutar la consulta de referencia: {e}",
                columnas_esperadas=[],
                filas_esperadas=[],
                columnas_obtenidas=[],
                filas_obtenidas=[],
                coinciden_columnas=False,
                coinciden_filas=False,
                mensaje="server-error",
                diagnostico="Error interno del servidor (la consulta de referencia falla).",
            )

        cols_esperadas = list(res_esperado.keys()) if res_esperado.returns_rows else []
        cols_obtenidas = list(res_usuario.keys()) if res_usuario.returns_rows else []

        filas_esperadas = (
            [dict(f) for f in res_esperado.mappings().all()[:limite]]
            if res_esperado.returns_rows else []
        )
        filas_obtenidas = (
            [dict(f) for f in res_usuario.mappings().all()[:limite]]
            if res_usuario.returns_rows else []
        )

        await tx.rollback()

    coinciden_columnas = cols_esperadas == cols_obtenidas or set(cols_esperadas) == set(cols_obtenidas)

    if orden_importa:
        coinciden_filas = filas_esperadas == filas_obtenidas
    else:
        coinciden_filas = _mismo_multiset(filas_esperadas, filas_obtenidas, cols_esperadas)

    ok = coinciden_columnas and coinciden_filas
    if ok:
        mensaje = "ok"
    elif not coinciden_columnas:
        mensaje = "wrong-columns"
    elif orden_importa:
        mensaje = "wrong-order"
    else:
        mensaje = "wrong-rows"

    diagnostico = ""
    if not ok:
        diagnostico = _diagnosticar(
            cols_esperadas, filas_esperadas,
            cols_obtenidas, filas_obtenidas,
            orden_importa, limite,
            caso=mensaje,
        )

    return ResultadoEjercicio(
        ok=ok,
        error=None,
        columnas_esperadas=cols_esperadas,
        filas_esperadas=filas_esperadas,
        columnas_obtenidas=cols_obtenidas,
        filas_obtenidas=filas_obtenidas,
        coinciden_columnas=coinciden_columnas,
        coinciden_filas=coinciden_filas,
        mensaje=mensaje,
        diagnostico=diagnostico,
    )


# ── Diagnóstico textual de filas / columnas / orden ──────────────────────────

def _diagnosticar(
    cols_esp: list[str],
    filas_esp: list[dict[str, Any]],
    cols_obt: list[str],
    filas_obt: list[dict[str, Any]],
    orden_importa: bool,
    limite: int,
    caso: str,
) -> str:
    n_esp = len(filas_esp)
    n_obt = len(filas_obt)
    cap_esp = "" if n_esp < limite else " (primeras {})".format(limite)
    cap_obt = "" if n_obt < limite else " (primeras {})".format(limite)

    if caso == "wrong-columns":
        set_esp = set(cols_esp)
        set_obt = set(cols_obt)
        faltan = sorted(set_esp - set_obt)
        sobran = sorted(set_obt - set_esp)
        partes = []
        if faltan and not sobran:
            partes.append("Tu consulta no devuelve columnas que se piden: " + ", ".join(faltan) + ".")
        elif sobran and not faltan:
            partes.append("Tu consulta devuelve columnas de más: " + ", ".join(sobran) + ".")
        elif faltan and sobran:
            partes.append("Faltan columnas: " + ", ".join(faltan) + "; y sobran: " + ", ".join(sobran) + ".")
        else:
            # mismo set, distinto orden
            partes.append("Las columnas son correctas pero están en otro orden.")
        return " ".join(partes)

    if caso == "wrong-order":
        return (
            "Las filas y los valores son correctos, pero el orden no coincide. "
            "Este ejercicio pide un ORDER BY concreto."
        )

    # caso == "wrong-rows"
    if n_obt == 0 and n_esp > 0:
        return (
            "Tu consulta no devuelve ninguna fila, pero se esperan {}{}. "
            "Revisa el nombre de la tabla/columna o tu WHERE."
        ).format(n_esp, cap_esp)
    if n_obt != n_esp:
        if n_obt > n_esp:
            return (
                "Tu consulta devuelve {}{} filas pero se esperan {}{}. "
                "Probablemente te falta un filtro (WHERE) o un LIMIT."
            ).format(n_obt, cap_obt, n_esp, cap_esp)
        return (
            "Tu consulta devuelve {}{} filas pero se esperan {}{}. "
            "Puede que tu WHERE filtre de más o que el JOIN descarte filas."
        ).format(n_obt, cap_obt, n_esp, cap_esp)
    # mismo conteo, valores distintos
    return (
        "Tu consulta devuelve {} filas (cantidad correcta) pero los valores no "
        "coinciden con los esperados. Compara tu resultado con la columna «Esperado»."
    ).format(n_obt)


# ── Traducción de errores PostgreSQL a español de principiante ──────────────

_PATRON_RELACION = re.compile(r'relation "([^"]+)" does not exist', re.IGNORECASE)
_PATRON_COLUMNA = re.compile(r'column "([^"]+)" does not exist', re.IGNORECASE)
_PATRON_SINTAXIS = re.compile(r'syntax error at or near "([^"]+)"', re.IGNORECASE)
_PATRON_AMBIGUA = re.compile(r'column reference "([^"]+)" is ambiguous', re.IGNORECASE)
_PATRON_FUNCION = re.compile(r'function ([^\s(]+\() does not exist', re.IGNORECASE)
_PATRON_OPERADOR = re.compile(r'operator does not exist:\s*(.*)', re.IGNORECASE)
_PATRON_SIN_COMILLAS = re.compile(r'unterminated quoted string', re.IGNORECASE)
_PATRON_DIV_CERO = re.compile(r'division by zero', re.IGNORECASE)
_PATRON_TIPO = re.compile(r'column "([^"]+)" is of type ([^ ]+) but', re.IGNORECASE)


def _traducir_error_pg(error: str) -> str:
    """Mapea los errores de PostgreSQL más comunes a un español para principiantes."""
    m = _PATRON_RELACION.search(error)
    if m:
        return (
            'La tabla «{}» no existe. Revisa el nombre: en SQL las mayúsculas/minúsculas '
            'importan en identificadores entre comillas.'
        ).format(m.group(1))
    m = _PATRON_COLUMNA.search(error)
    if m:
        return (
            'La columna «{}» no existe en esa tabla. Revisa el nombre o de qué tabla la estás pidiendo.'
        ).format(m.group(1))
    m = _PATRON_AMBIGUA.search(error)
    if m:
        return (
            'La columna «{}» existe en varias tablas del JOIN. '
            'Cualifícala con el formato tabla.columna (p. ej. libros.titulo).'
        ).format(m.group(1))
    m = _PATRON_SINTAXIS.search(error)
    if m:
        return (
            'Error de sintaxis cerca de «{}». '
            'Revisa comillas, paréntesis y palabras clave (SELECT, FROM, WHERE…).'
        ).format(m.group(1))
    m = _PATRON_FUNCION.search(error)
    if m:
        return (
            'La función «{}» no existe. ¿Será un error de tipeo o de mayúsculas? '
            'En SQL las funciones suelen escribirse en minúsculas.'
        ).format(m.group(1).rstrip("("))
    m = _PATRON_OPERADOR.search(error)
    if m:
        return (
            "Ese operador no existe o no se aplica entre esos tipos de datos. "
            "Revisa el operador y los tipos de las columnas que comparas."
        )
    if _PATRON_SIN_COMILLAS.search(error):
        return "Falta cerrar una comilla simple (') en algún valor de texto."
    if _PATRON_DIV_CERO.search(error):
        return "División por cero: estás dividiendo por una columna o valor que es 0."
    m = _PATRON_TIPO.search(error)
    if m:
        return (
            'La columna «{}» es de tipo {} pero se está usando con un tipo incompatible. '
            'Revisa que estés comparando tipos correctos (texto vs número, etc.).'
        ).format(m.group(1), m.group(2))
    # Fallback genérico: primera línea del error, recortada
    primera = error.strip().split("\n")[0]
    if len(primera) > 180:
        primera = primera[:180] + "…"
    return "PostgreSQL rechazó tu consulta: " + primera


def _traducir_error_validacion(error: str) -> str:
    """Errores del validador de seguridad (no SELECT, contiene DROP, etc.)."""
    if "Solo se permiten consultas de lectura" in error:
        return (
            "Solo se permiten consultas de lectura (SELECT, WITH, EXPLAIN). "
            "Esta consola no acepta INSERT/UPDATE/DELETE ni DDL."
        )
    if "multiples sentencias" in error:
        return "No se permiten varias sentencias seguidas (no uses punto y coma en medio)."
    if "vacia" in error:
        return "Escribe una consulta antes de probar."
    if "prohibidas" in error.lower():
        return "Tu consulta incluye palabras prohibidas (INSERT, DROP, ALTER…). Esta consola es de solo lectura."
    return error


def _mismo_multiset(
    filas_a: list[dict[str, Any]],
    filas_b: list[dict[str, Any]],
    cols: list[str],
) -> bool:
    """Compara como multiconjunto: misma cantidad y mismas tuplas (sin orden)."""
    if len(filas_a) != len(filas_b):
        return False
    keys = list(cols) if cols else (list(filas_a[0].keys()) if filas_a else [])
    a_sorted = sorted([tuple(_norm(f.get(k)) for k in keys) for f in filas_a])
    b_sorted = sorted([tuple(_norm(f.get(k)) for k in keys) for f in filas_b])
    return a_sorted == b_sorted


def _norm(v: Any) -> Any:
    """Normaliza para comparación: None se vuelve '<<NULL>>'."""
    if v is None:
        return "\x00NULL\x00"
    return v