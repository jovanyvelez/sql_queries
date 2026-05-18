import re

PELIGROSAS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "COPY", "GRANT", "REVOKE", "VACUUM", "REINDEX",
    "DISCARD", "REASSIGN", "REFRESH", "SECURITY", "IMPORT",
    "LISTEN", "NOTIFY", "UNLISTEN", "MOVE", "FETCH", "CLOSE",
    "PREPARE", "EXECUTE", "DEALLOCATE", "DECLARE",
}

PERMITIDAS = {"SELECT", "WITH", "EXPLAIN"}


_RE_DOLAR = re.compile(r"\$[a-zA-Z_]\w*\$[\s\S]*?\$[a-zA-Z_]\w*\$")
_RE_COMILLAS = re.compile(r"'(?:[^']|'')*'")
_RE_E_STRING = re.compile(r"[eE]'(?:[^'\\]|\\.|'')*'")
_RE_COMENTARIO_LINEA = re.compile(r"--[^\n]*")
_RE_COMENTARIO_BLOQUE = re.compile(r"/\*[\s\S]*?\*/")
_RE_PALABRAS = re.compile(r"\b[A-Z]+\b")


def validar_consulta(sql: str) -> str:
    limpio = sql.strip()

    if not limpio:
        raise ValueError("La consulta esta vacia")

    if ";" in limpio:
        raise ValueError("No se permiten multiples sentencias (;)")

    sin_literales = _eliminar_literales(limpio)

    primera = sin_literales.split(None, 1)[0].upper()
    if primera not in PERMITIDAS:
        raise ValueError(f"Solo se permiten consultas de lectura (SELECT, WITH, EXPLAIN)")

    palabras = set(_RE_PALABRAS.findall(sin_literales.upper()))
    prohibidas = palabras & PELIGROSAS
    if prohibidas:
        raise ValueError(f"Palabras prohibidas detectadas: {', '.join(sorted(prohibidas))}")

    return limpio


def _eliminar_literales(sql: str) -> str:
    sql = _RE_COMENTARIO_LINEA.sub("", sql)
    sql = _RE_COMENTARIO_BLOQUE.sub("", sql)
    sql = _RE_E_STRING.sub("''", sql)
    sql = _RE_DOLAR.sub("''", sql)
    sql = _RE_COMILLAS.sub("''", sql)
    return sql
