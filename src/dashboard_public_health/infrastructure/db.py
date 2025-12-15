# infrastructure/sqlite_repository.py
# src/dashboard_public_health/infrastructure/db.py
from __future__ import annotations

from dashboard_public_health.domain.models import HealthRecord
import sqlite3
from typing import Iterable, Dict, Any, Optional

from dashboard_public_health import config
from time import perf_counter
from dashboard_public_health.infrastructure.logger import logger


def get_conn() -> sqlite3.Connection:
    """
    Always use config.DB_PATH so pytest monkeypatch can redirect the DB.
    """
    db_path = config.DB_PATH
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
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL,
            year INTEGER NOT NULL,
            disease TEXT NOT NULL,
            disease_category TEXT,
            prevalence_rate REAL,
            incidence_rate REAL,
            mortality_rate REAL,
            population_affected REAL,
            recovery_rate REAL,
            dalys REAL,
            healthcare_access REAL,
            doctors_per_1000 REAL,
            hospital_beds_per_1000 REAL,
            per_capita_income REAL,
            education_index REAL,
            urbanization_rate REAL,
            age_group TEXT,
            gender TEXT,
            treatment_available TEXT,
            source_file TEXT,   -- Optional: source CSV name
                    -- Optional: store extra fields
                    -- extra_json TEXT,
            UNIQUE(country, year, disease, disease_category, age_group, gender,source_file)
        )
        """
    )
    conn.commit()

    if own_conn:
        conn.close()


def insert_records(records, conn):
    """
    Insert cleaned internal-schema record into SQLite.
    Accepts iterable of dicts or HealthRecord instances.
    Avoid duplicate insertions using UNIQUE constraint.
    """

    cur = conn.cursor()
    start = perf_counter()

    sql = """
        INSERT OR IGNORE INTO records (
            country,
            year,
            disease,
            disease_category,
            prevalence_rate,
            incidence_rate,
            mortality_rate,
            population_affected,
            recovery_rate,
            dalys,
            healthcare_access,
            doctors_per_1000,
            hospital_beds_per_1000,
            per_capita_income,
            education_index,
            urbanization_rate,
            age_group,
            gender,
            treatment_available,
            source_file
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    def to_tuple(r):
        if isinstance(r, HealthRecord):
            return r.to_db_tuple()
        # assume mapping/dict
        return (
            r.get("country"),
            r.get("year"),
            r.get("disease"),
            r.get("disease_category"),
            r.get("prevalence_rate"),
            r.get("incidence_rate"),
            r.get("mortality_rate"),
            r.get("population_affected"),
            r.get("recovery_rate"),
            r.get("dalys"),
            r.get("healthcare_access"),
            r.get("doctors_per_1000"),
            r.get("hospital_beds_per_1000"),
            r.get("per_capita_income"),
            r.get("education_index"),
            r.get("urbanization_rate"),
            r.get("age_group"),
            r.get("gender"),
            r.get("treatment_available"),
            r.get("source_file"),
        )

    rows = [to_tuple(r) for r in records]

    cur.executemany(sql, rows)
    conn.commit()

    duration = perf_counter() - start
    logger.info(f"[perf] insert_records duration={duration:.4f}s rows={cur.rowcount}")
    print(f"[db] Inserted {cur.rowcount} new rows (duplicates ignored).")


def insert_record(record, conn=None):
    """Insert a single record (dict or HealthRecord)."""
    own_conn = False
    if conn is None:
        conn = get_conn()
        own_conn = True
    insert_records([record], conn)
    last_id = None
    try:
        last_id = conn.execute("SELECT last_insert_rowid();").fetchone()[0]
    except Exception:
        last_id = None
    if own_conn:
        conn.close()
    return last_id


def get_record_by_id(record_id: int, conn=None) -> Optional[HealthRecord]:
    own_conn = False
    if conn is None:
        conn = get_conn()
        own_conn = True

    cur = conn.cursor()
    cur.execute("SELECT * FROM records WHERE id = ?", (record_id,))
    row = cur.fetchone()
    if row is None:
        if own_conn:
            conn.close()
        return None

    columns = [col[0] for col in cur.description]
    data = dict(zip(columns, row))
    record = HealthRecord.from_dict(data)

    if own_conn:
        conn.close()
    return record


def update_record_by_id(record_id: int, updates: Dict[str, Any], conn=None) -> int:
    """Update fields for a given record id. Returns affected row count."""
    own_conn = False
    if conn is None:
        conn = get_conn()
        own_conn = True

    if not updates:
        return 0

    columns, params = zip(*[(f"{k} = ?", v) for k, v in updates.items()])
    sql = f"UPDATE records SET {', '.join(columns)} WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, (*params, record_id))
    conn.commit()

    count = cur.rowcount
    if own_conn:
        conn.close()
    return count


def delete_record_by_id(record_id: int, conn=None) -> int:
    own_conn = False
    if conn is None:
        conn = get_conn()
        own_conn = True

    cur = conn.cursor()
    cur.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    count = cur.rowcount

    if own_conn:
        conn.close()
    return count


def drop_all_records(conn):
    """Development-only: clear the entire table before re-ingestion."""
    cur = conn.cursor()
    cur.execute("DELETE FROM records;")
    conn.commit()
    print("[db] Cleared existing records (development mode).")
