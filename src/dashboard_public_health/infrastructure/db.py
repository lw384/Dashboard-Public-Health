# infrastructure/sqlite_repository.py
# src/dashboard_public_health/infrastructure/db.py
from __future__ import annotations

from dashboard_public_health.domain.models import Record
import sqlite3
from typing import Iterable, Dict, Any, Optional

from dashboard_public_health import config


def get_conn() -> sqlite3.Connection:
    """
    Always use config.DB_PATH so pytest monkeypatch can redirect the DB.
    """
    db_path = config.DB_PATH  # ⚠️ 关键：每次从 config 读取
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_db_schema(conn: Optional[sqlite3.Connection] = None) -> None:
    """
    Create the 'record' table if it does not exist.
    If conn is None, open and close an internal connection.
    """
    own_conn = False
    if conn is None:
        conn = get_conn()
        own_conn = True

    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            country TEXT NOT NULL,
            indicator TEXT NOT NULL,
            value REAL NOT NULL,
            age_group TEXT,
            source_file TEXT,   -- 可选：记录来自哪个 CSV
            -- 可选：存多余字段
            -- extra_json TEXT,
            UNIQUE(date, country, indicator, age_group, source_file)
        );
        """
    )
    conn.commit()

    if own_conn:
        conn.close()


def insert_records(
    records: Iterable[Dict[str, Any]],
    conn: Optional[sqlite3.Connection] = None,
) -> None:
    """
    Insert multiple records into 'record'.

    Each record dict must have:
      - date, country, indicator, value
      - age_group, source_file (optional)
    """
    own_conn = False
    if conn is None:
        conn = get_conn()
        own_conn = True

    cur = conn.cursor()

    rows = [
        (
            r["date"],
            r["country"],
            r["indicator"],
            r["value"],
            r.get("age_group"),
            r.get("source_file"),
        )
        for r in records
    ]

    cur.executemany(
        """
        INSERT OR IGNORE INTO record
        (date, country, indicator, value, age_group, source_file)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()

    if own_conn:
        conn.close()
    print(f"[db] Inserted {cur.rowcount} new rows (duplicates ignored).")


def fetch_all_records():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT country, year, value FROM record")
    rows = cur.fetchall()
    conn.close()
    return [
        Record(country=row[0], year=row[1], metric_name=row[2], value=row[3])
        for row in rows
    ]
