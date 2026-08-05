import re

PELIGROSAS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "COPY", "GRANT", "REVOKE", "VACUUM", "REINDEX",
    "DISCARD", "REASSIGN", "REFRESH", "SECURITY", "IMPORT",
    "LISTEN", "NOTIFY", "UNLISTEN", "MOVE", "FETCH", "CLOSE",
    "PREPARE", "EXECUTE", "DEALLOCATE", "DECLARE",
}

PERMITIDAS = {"SELECT", "WITH", "EXPLAIN"}

# Esquemas permitidos para SET search_path desde la consola interactiva.
# Vacío = cualquier esquema (se valida contra la lista de psets + public).
ESQUEMAS_PERMITIDOS = {"public", "dese", "moneyball", "packages"}

_RE_DOLAR = re.compile(r"\$[a-zA-Z_]\w*\$[\s\S]*?\$[a-zA-Z_]\w*\$")
_RE_COMILLAS = re.compile(r"'(?:[^']|'')*'")
_RE_E_STRING = re.compile(r"[eE]'(?:[^'\\]|\\.|'')*'")
_RE_COMENTARIO_LINEA = re.compile(r"--[^\n]*")
_RE_COMENTARIO_BLOQUE = re.compile(r"/\*[\s\S]*?\*/")
_RE_PALABRAS = re.compile(r"\b[A-Z]+\b")
_RE_SEARCH_PATH = re.compile(
    r"^\s*SET\s+search_path\s+TO\s+([A-Za-z_][\w]*)\s*;?\s*",
    re.IGNORECASE,
)


def validar_consulta(sql: str) -> str:
    """Valida y normaliza una consulta SQL de solo lectura.

    Acepta un prefijo opcional `SET search_path TO <esquema>;` (solo si el
    esquema está en ESQUEMAS_PERMITIDOS). El prefijo se devuelve aparte vía
    `extraer_search_path`, y esta función devuelve el SQL sin el prefijo.
    """
    limpio = sql.strip()

    if not limpio:
        raise ValueError("La consulta esta vacia")

    # Extraer y validar SET search_path TO ... (prefijo opcional)
    m = _RE_SEARCH_PATH.match(limpio)
    if m:
        esquema = m.group(1).lower()
        if esquema not in ESQUEMAS_PERMITIDOS:
            raise ValueError(
                f"Esquema no permitido: {esquema}. "
                f"Permitidos: {', '.join(sorted(ESQUEMAS_PERMITIDOS))}"
            )
        # quitar el prefijo para analizar el resto
        limpio = limpio[m.end():].strip()
        if not limpio:
            raise ValueError("Falta la consulta despues de SET search_path")

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


def extraer_search_path(sql: str) -> tuple[str | None, str]:
    """Devuelve (esquema_o_None, sql_restante).

    Si la consulta empieza con `SET search_path TO <esq>;`, devuelve el
    esquema y el SQL sin el prefijo. Si no, devuelve (None, sql_original).
    """
    limpio = sql.strip()
    m = _RE_SEARCH_PATH.match(limpio)
    if m:
        esquema = m.group(1).lower()
        if esquema in ESQUEMAS_PERMITIDOS:
            return esquema, limpio[m.end():].strip()
    return None, limpio


def _eliminar_literales(sql: str) -> str:
    sql = _RE_COMENTARIO_LINEA.sub("", sql)
    sql = _RE_COMENTARIO_BLOQUE.sub("", sql)
    sql = _RE_E_STRING.sub("''", sql)
    sql = _RE_DOLAR.sub("''", sql)
    sql = _RE_COMILLAS.sub("''", sql)
    return sql
