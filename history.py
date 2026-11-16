"""
A small local history store, so a refresh does not throw away work.

Everything lives in one SQLite file on the machine running the app:
``.docentry/history.db`` by default, or ``DOCENTRY_HISTORY_DB`` if set.
On Streamlit Community Cloud that file is temporary, but it still keeps the
session usable and is enough for a single-user deployment.
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent / ".docentry" / "history.db"


def db_path() -> Path:
    override = os.getenv("DOCENTRY_HISTORY_DB")
    return Path(override).expanduser() if override else DEFAULT_DB


def _connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def _init(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at    TEXT NOT NULL,
            doc_type      TEXT NOT NULL,
            label         TEXT NOT NULL,
            row_count     INTEGER NOT NULL DEFAULT 0,
            columns_json  TEXT NOT NULL,
            rows_json     TEXT NOT NULL,
            issues_json   TEXT NOT NULL DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS presets (
            name          TEXT PRIMARY KEY,
            created_at    TEXT NOT NULL,
            columns_json  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS doc_types (
            name          TEXT PRIMARY KEY,
            created_at    TEXT NOT NULL,
            columns_json  TEXT NOT NULL
        );
        """
    )
    connection.commit()


def available() -> bool:
    try:
        with closing(_connect()) as connection:
            _init(connection)
        return True
    except Exception:  # noqa: BLE001 - history must never break extraction
        return False


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --------------------------------------------------------------------------
# Runs
# --------------------------------------------------------------------------

def save_run(
    doc_type: str,
    rows: list[dict],
    columns: list[tuple[str, str]],
    issues: list[dict] | None = None,
    label: str = "",
) -> int:
    label = (label or "").strip() or f"{doc_type} · {len(rows)} row(s)"
    with closing(_connect()) as connection:
        _init(connection)
        cursor = connection.execute(
            """
            INSERT INTO runs
                (created_at, doc_type, label, row_count, columns_json, rows_json, issues_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                _now(),
                doc_type,
                label,
                len(rows),
                json.dumps(columns, ensure_ascii=False),
                json.dumps(rows, ensure_ascii=False),
                json.dumps(issues or [], ensure_ascii=False),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def list_runs(limit: int = 30) -> list[dict]:
    with closing(_connect()) as connection:
        _init(connection)
        rows = connection.execute(
            """
            SELECT id, created_at, doc_type, label, row_count
            FROM runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_run(run_id: int) -> dict | None:
    with closing(_connect()) as connection:
        _init(connection)
        row = connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "doc_type": row["doc_type"],
        "label": row["label"],
        "columns": [tuple(column) for column in json.loads(row["columns_json"])],
        "rows": json.loads(row["rows_json"]),
        "issues": json.loads(row["issues_json"] or "[]"),
    }


def delete_run(run_id: int) -> None:
    with closing(_connect()) as connection:
        _init(connection)
        connection.execute("DELETE FROM runs WHERE id = ?", (run_id,))
        connection.commit()


def clear_runs() -> None:
    with closing(_connect()) as connection:
        _init(connection)
        connection.execute("DELETE FROM runs")
        connection.commit()


# --------------------------------------------------------------------------
# Column presets
# --------------------------------------------------------------------------

def save_preset(name: str, columns: list[tuple[str, str]]) -> None:
    name = (name or "").strip()
    if not name:
        raise ValueError("A preset needs a name.")
    with closing(_connect()) as connection:
        _init(connection)
        connection.execute(
            """
            INSERT INTO presets (name, created_at, columns_json)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                created_at = excluded.created_at,
                columns_json = excluded.columns_json
            """,
            (name, _now(), json.dumps(columns, ensure_ascii=False)),
        )
        connection.commit()


def list_presets() -> list[dict]:
    with closing(_connect()) as connection:
        _init(connection)
        rows = connection.execute(
            "SELECT name, created_at, columns_json FROM presets ORDER BY name"
        ).fetchall()
    return [
        {
            "name": row["name"],
            "created_at": row["created_at"],
            "columns": [tuple(column) for column in json.loads(row["columns_json"])],
        }
        for row in rows
    ]


def delete_preset(name: str) -> None:
    with closing(_connect()) as connection:
        _init(connection)
        connection.execute("DELETE FROM presets WHERE name = ?", (name,))
        connection.commit()


# --------------------------------------------------------------------------
# User-defined document types
# --------------------------------------------------------------------------

def save_doc_type(name: str, columns: list[tuple[str, str]]) -> None:
    name = (name or "").strip()
    if not name:
        raise ValueError("A document type needs a name.")
    with closing(_connect()) as connection:
        _init(connection)
        connection.execute(
            """
            INSERT INTO doc_types (name, created_at, columns_json)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                created_at = excluded.created_at,
                columns_json = excluded.columns_json
            """,
            (name, _now(), json.dumps(columns, ensure_ascii=False)),
        )
        connection.commit()


def list_doc_types() -> dict[str, list[tuple[str, str]]]:
    with closing(_connect()) as connection:
        _init(connection)
        rows = connection.execute(
            "SELECT name, columns_json FROM doc_types ORDER BY name"
        ).fetchall()
    return {
        row["name"]: [tuple(column) for column in json.loads(row["columns_json"])]
        for row in rows
    }


def delete_doc_type(name: str) -> None:
    with closing(_connect()) as connection:
        _init(connection)
        connection.execute("DELETE FROM doc_types WHERE name = ?", (name,))
        connection.commit()
