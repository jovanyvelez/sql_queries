"""Migración única de los 3 psets de CS50 SQL (SQLite) a PostgreSQL.

Crea los esquemas `dese`, `moneyball` y `packages` y vuelca las tablas desde
los archivos .db descargados de Harvard. Es idempotente: si las tablas ya
existen, las omite (a menos que se pase --force).

Uso:
    python migrar_psets.py            # migra los 3
    python migrar_psets.py dese        # solo uno
    python migrar_psets.py --force     # recrea (DROP + CREATE) antes de cargar
"""

from __future__ import annotations

import asyncio
import os
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import asyncpg
from dotenv import load_dotenv

load_dotenv()

# ── Configuración ────────────────────────────────────────────────────────────

PSETS_DIR = Path(__file__).resolve().parent / "psets_data"

DATABASE_URL = os.getenv("DATABASE_URL", "")
# asyncpg necesita una URL postgres:// (no sqlalchemy+asyncpg://)
PG_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgres://").replace(
    "postgresql://", "postgres://"
)


@dataclass
class ColumnDef:
    name: str
    pg_type: str  # tipo SQL de PostgreSQL (sin comillas)
    is_pk: bool = False


@dataclass
class TableDef:
    name: str
    columns: list[ColumnDef]
    foreign_keys: list[tuple[str, str, str]] = field(default_factory=list)  # (col, ref_table, ref_col)


# ── Definición de esquemas (fiel a los .db originales) ───────────────────────

DESE_TABLES: list[TableDef] = [
    TableDef(
        "districts",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("name", "TEXT"),
            ColumnDef("type", "TEXT"),
            ColumnDef("city", "TEXT"),
            ColumnDef("state", "TEXT"),
            ColumnDef("zip", "TEXT"),
        ],
    ),
    TableDef(
        "schools",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("district_id", "INTEGER"),
            ColumnDef("name", "TEXT"),
            ColumnDef("type", "TEXT"),
            ColumnDef("city", "TEXT"),
            ColumnDef("state", "TEXT"),
            ColumnDef("zip", "TEXT"),
        ],
        foreign_keys=[("district_id", "districts", "id")],
    ),
    TableDef(
        "graduation_rates",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("school_id", "INTEGER"),
            ColumnDef("graduated", "NUMERIC"),
            ColumnDef("dropped", "NUMERIC"),
            ColumnDef("excluded", "NUMERIC"),
        ],
        foreign_keys=[("school_id", "schools", "id")],
    ),
    TableDef(
        "expenditures",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("district_id", "INTEGER"),
            ColumnDef("pupils", "INTEGER"),
            ColumnDef("per_pupil_expenditure", "NUMERIC"),
        ],
        foreign_keys=[("district_id", "districts", "id")],
    ),
    TableDef(
        "staff_evaluations",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("district_id", "INTEGER"),
            ColumnDef("evaluated", "NUMERIC"),
            ColumnDef("exemplary", "NUMERIC"),
            ColumnDef("proficient", "NUMERIC"),
            ColumnDef("needs_improvement", "NUMERIC"),
            ColumnDef("unsatisfactory", "NUMERIC"),
        ],
        foreign_keys=[("district_id", "districts", "id")],
    ),
]

MONEYBALL_TABLES: list[TableDef] = [
    TableDef(
        "players",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("first_name", "TEXT"),
            ColumnDef("last_name", "TEXT"),
            ColumnDef("bats", "TEXT"),
            ColumnDef("throws", "TEXT"),
            ColumnDef("weight", "INTEGER"),
            ColumnDef("height", "INTEGER"),
            ColumnDef("debut", "TEXT"),  # YYYY-MM-DD
            ColumnDef("final_game", "TEXT"),
            ColumnDef("birth_year", "INTEGER"),
            ColumnDef("birth_month", "INTEGER"),
            ColumnDef("birth_day", "INTEGER"),
            ColumnDef("birth_city", "TEXT"),
            ColumnDef("birth_state", "TEXT"),
            ColumnDef("birth_country", "TEXT"),
        ],
    ),
    TableDef(
        "teams",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("year", "INTEGER"),
            ColumnDef("name", "TEXT"),
            ColumnDef("park", "TEXT"),
        ],
    ),
    TableDef(
        "salaries",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("player_id", "INTEGER"),
            ColumnDef("team_id", "INTEGER"),
            ColumnDef("year", "INTEGER"),
            ColumnDef("salary", "INTEGER"),
        ],
        foreign_keys=[
            ("player_id", "players", "id"),
            ("team_id", "teams", "id"),
        ],
    ),
    TableDef(
        "performances",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("player_id", "INTEGER"),
            ColumnDef("team_id", "INTEGER"),
            ColumnDef("year", "INTEGER"),
            ColumnDef("G", "INTEGER"),
            ColumnDef("AB", "INTEGER"),
            ColumnDef("H", "INTEGER"),
            ColumnDef("2B", "INTEGER"),  # necesita comillas
            ColumnDef("3B", "INTEGER"),
            ColumnDef("HR", "INTEGER"),
            ColumnDef("RBI", "INTEGER"),
            ColumnDef("SB", "INTEGER"),
        ],
        foreign_keys=[
            ("player_id", "players", "id"),
            ("team_id", "teams", "id"),
        ],
    ),
]

PACKAGES_TABLES: list[TableDef] = [
    TableDef(
        "addresses",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("address", "TEXT"),
            ColumnDef("type", "TEXT"),
        ],
    ),
    TableDef(
        "packages",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("contents", "TEXT"),
            ColumnDef("from_address_id", "INTEGER"),
            ColumnDef("to_address_id", "INTEGER"),
        ],
        foreign_keys=[
            ("from_address_id", "addresses", "id"),
            ("to_address_id", "addresses", "id"),
        ],
    ),
    TableDef(
        "drivers",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("name", "TEXT"),
        ],
    ),
    TableDef(
        "scans",
        [
            ColumnDef("id", "INTEGER", is_pk=True),
            ColumnDef("driver_id", "INTEGER"),
            ColumnDef("package_id", "INTEGER"),
            ColumnDef("address_id", "INTEGER"),
            ColumnDef("action", "TEXT"),
            ColumnDef("timestamp", "TEXT"),  # texto ISO-like
        ],
        foreign_keys=[
            ("driver_id", "drivers", "id"),
            ("package_id", "packages", "id"),
            ("address_id", "addresses", "id"),
        ],
    ),
]

PSETS = {
    "dese": DESE_TABLES,
    "moneyball": MONEYBALL_TABLES,
    "packages": PACKAGES_TABLES,
}


# ── Utilidades SQL ───────────────────────────────────────────────────────────


def _col_ref(name: str) -> str:
    """Identificador seguro: algunos nombres (2B, 3B) requieren comillas."""
    if not name.isidentifier():
        return f'"{name}"'
    return name


def _ddl_for_table(schema: str, t: TableDef) -> str:
    cols_sql = []
    for c in t.columns:
        parts = [f"{_col_ref(c.name)} {c.pg_type}"]
        if c.is_pk:
            parts.append("PRIMARY KEY")
        cols_sql.append(" ".join(parts))
    for col, ref_t, ref_c in t.foreign_keys:
        cols_sql.append(
            f"FOREIGN KEY ({_col_ref(col)}) "
            f"REFERENCES {schema}.{ref_t}({_col_ref(ref_c)})"
        )
    return (
        f'CREATE TABLE IF NOT EXISTS {schema}.{t.name} (\n'
        + ",\n".join("    " + s for s in cols_sql)
        + "\n)"
    )


def _drop_ddl(schema: str, t: TableDef) -> str:
    return f"DROP TABLE IF EXISTS {schema}.{t.name} CASCADE"


# ── Migración ────────────────────────────────────────────────────────────────


def _read_sqlite_rows(db_path: Path, table: str, columns: list[str]) -> list[list[Any]]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = None
    col_list = ", ".join(_col_ref(c.name) for c in columns)
    cur = conn.execute(f"SELECT {col_list} FROM {table}")
    rows = cur.fetchall()
    conn.close()
    return rows


async def _migrate_pset(
    conn: asyncpg.Connection,
    schema: str,
    tables: list[TableDef],
    db_path: Path,
    force: bool,
) -> None:
    print(f"\n=== Migrando {schema} ===")
    print(f"  Fuente SQLite: {db_path}")

    await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    for t in tables:
        if force:
            print(f"  [DROP] {schema}.{t.name}")
            await conn.execute(_drop_ddl(schema, t))

        print(f"  [CREATE] {schema}.{t.name}")
        await conn.execute(_ddl_for_table(schema, t))

    # Insertar datos (respetando orden de FKs: padres antes que hijas)
    for t in tables:
        rows = _read_sqlite_rows(db_path, t.name, t.columns)
        print(f"  [COPY] {schema}.{t.name}: {len(rows)} filas")

        if not rows:
            continue

        col_refs = [_col_ref(c.name) for c in t.columns]
        col_list_sql = ", ".join(col_refs)
        placeholders = ", ".join(f"${i+1}" for i in range(len(col_refs)))
        insert_sql = (
            f"INSERT INTO {schema}.{t.name} ({col_list_sql}) "
            f"VALUES ({placeholders})"
        )
        # Insertar en lotes para no saturar
        batch = 1000
        for i in range(0, len(rows), batch):
            chunk = rows[i : i + batch]
            await conn.executemany(insert_sql, chunk)

        # Reiniciar secuencia/sync — no usamos SERIAL aquí, los id vienen de SQLite


async def _verify_counts(
    conn: asyncpg.Connection,
    schema: str,
    tables: list[TableDef],
    db_path: Path,
) -> None:
    print(f"\n--- Verificación {schema} (SQLite vs PostgreSQL) ---")
    sqlite_conn = sqlite3.connect(str(db_path))
    for t in tables:
        sqlite_n = sqlite_conn.execute(f"SELECT COUNT(*) FROM {t.name}").fetchone()[0]
        pg_n = await conn.fetchval(f"SELECT COUNT(*) FROM {schema}.{t.name}")
        status = "OK" if sqlite_n == pg_n else "DIFF!"
        print(f"  {t.name}: sqlite={sqlite_n} pg={pg_n}  [{status}]")
    sqlite_conn.close()


async def main(argv: list[str]) -> int:
    force = "--force" in argv
    targets = [a for a in argv if not a.startswith("-")]

    if not PG_URL:
        print("ERROR: DATABASE_URL no configurada en .env", file=sys.stderr)
        return 1

    if not PSETS_DIR.exists():
        print(f"ERROR: no existe {PSETS_DIR}", file=sys.stderr)
        print("  Descarga los ZIP de Harvard y descomprímelos ahí:")
        for slug in PSETS:
            print(f"    wget https://cdn.cs50.net/sql/2024/x/psets/1/{slug}.zip")
            print(f"    unzip {slug}.zip -d psets_data/")
        return 1

    if not targets:
        targets = list(PSETS.keys())

    print(f"Conectando a PostgreSQL…")
    print(f"  URL (oculta): {PG_URL.split('@')[0].rsplit(':', 1)[0]}:***@{PG_URL.split('@')[1]}")

    conn = await asyncpg.connect(PG_URL)
    try:
        for slug in targets:
            if slug not in PSETS:
                print(f"  (ignorado) pset desconocido: {slug}")
                continue
            db_path = PSETS_DIR / slug / f"{slug}.db"
            if not db_path.exists():
                print(f"  (ignorado) no se encuentra {db_path}")
                continue
            await _migrate_pset(conn, slug, PSETS[slug], db_path, force)
            await _verify_counts(conn, slug, PSETS[slug], db_path)

        print("\nMigración completa.")
    finally:
        await conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main(sys.argv[1:])))