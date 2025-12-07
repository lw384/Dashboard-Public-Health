# infrastructure/sqlite_repository.py
import sqlite3
from typing import Iterable
from dashboard_public_health.domain.models import Record

from dashboard_public_health.config import DB_PATH


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db_schema():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT,
            year INTEGER,
            metric_name TEXT,
            value REAL
        )
    """
    )
    conn.commit()
    conn.close()


def insert_records(records: Iterable[Record]):
    conn = get_conn()
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO records (country, year, metric_name, value) VALUES (?, ?, ?, ?)",
        [(r.country, r.year, r.metric_name, r.value) for r in records],
    )
    conn.commit()
    conn.close()


def fetch_all_records():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT country, year, metric_name, value FROM records")
    rows = cur.fetchall()
    conn.close()
    return [
        Record(country=row[0], year=row[1], metric_name=row[2], value=row[3])
        for row in rows
    ]
