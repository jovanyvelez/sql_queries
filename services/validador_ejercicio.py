"""Validador de ejercicios: compara el resultado del usuario con el esperado."""

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


async def probar_ejercicio(
    db: AsyncSession,
    sql_usuario: str,
    sql_esperado: str,
    orden_importa: bool,
    limite: int = 200,
) -> ResultadoEjercicio:
    """Ejecuta ambas consultas en una transacción READ ONLY y compara resultados.

    - Comparación de columnas: mismas columnas (como set) en el mismo orden.
    - Comparación de filas: si orden_importa, comparación estricta en orden.
      Si no, comparación como multiconjunto (sorted) ignorando el orden de filas.
    - Se limita a `limite` filas por consulta para evitar resultados enormes.
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
        )

    async with db.begin() as tx:
        await db.execute(text("SET TRANSACTION READ ONLY"))

        try:
            res_usuario = await db.execute(text(consulta_usuario))
        except Exception as e:
            await tx.rollback()
            return ResultadoEjercicio(
                ok=False,
                error=f"Error al ejecutar tu consulta: {e}",
                columnas_esperadas=[],
                filas_esperadas=[],
                columnas_obtenidas=[],
                filas_obtenidas=[],
                coinciden_columnas=False,
                coinciden_filas=False,
                mensaje="execution-error",
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
    )


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