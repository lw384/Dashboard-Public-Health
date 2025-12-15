# tests/infra/test_db.py
from dashboard_public_health.infrastructure.db import (
    get_conn,
    init_db_schema,
    insert_records,
    insert_record,
    get_record_by_id,
    update_record_by_id,
    delete_record_by_id,
)
from dashboard_public_health.domain.models import HealthRecord
from dashboard_public_health.infrastructure.logger import logger
import logging


# -------------------------------------------------------------
# 1. Test DB schema is created correctly
# -------------------------------------------------------------
def test_init_db_creates_table(temp_db_path):
    conn = get_conn()
    init_db_schema(conn)

    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='records';"
    )
    row = cursor.fetchone()

    assert row is not None
    conn.close()


# -------------------------------------------------------------
# 2. Test INSERT + UNIQUE dedup logic
# -------------------------------------------------------------
def test_insert_records_inserts_and_ignores_duplicates(temp_db_path):
    conn = get_conn()
    init_db_schema(conn)

    # Build a valid record per the internal schema
    rec1 = {
        "country": "UK",
        "year": 2020,
        "disease": "Flu",
        "disease_category": "Infectious",
        "prevalence_rate": 12.5,
        "incidence_rate": 2.5,
        "mortality_rate": 0.3,
        "population_affected": 150000,
        "recovery_rate": 95.2,
        "dalys": 1000,
        "healthcare_access": 90.0,
        "doctors_per_1000": 3.5,
        "hospital_beds_per_1000": 2.0,
        "per_capita_income": 32000,
        "education_index": 0.92,
        "urbanization_rate": 85.0,
        "age_group": "18-49",
        "gender": "Both",
        "treatment_available": "Yes",
        "source_file": "test.csv",
    }

    # duplicate based on UNIQUE(country, year, disease, disease_category, age_group, gender)
    rec2 = rec1.copy()

    records = [rec1, rec2]

    insert_records(records, conn)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM records;")
    (count,) = cursor.fetchone()

    # After deduplication, only 1 row should remain
    assert count == 1

    conn.close()


def test_insert_records_accepts_healthrecord(temp_db_path):
    conn = get_conn()
    init_db_schema(conn)

    rec = HealthRecord(
        country="Spain",
        year=2020,
        disease="Flu",
        disease_category="Viral",
        prevalence_rate=5.0,
        incidence_rate=3.0,
        mortality_rate=1.0,
        population_affected=1000,
        recovery_rate=90.0,
        dalys=200.0,
        healthcare_access=70.0,
        doctors_per_1000=3.0,
        hospital_beds_per_1000=4.0,
        per_capita_income=30000.0,
        education_index=0.7,
        urbanization_rate=60.0,
        age_group="18-49",
        gender="Male",
        treatment_available="Yes",
        source_file="test.csv",
    )

    insert_records([rec], conn)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM records WHERE country='Spain';")
    (count,) = cursor.fetchone()
    conn.close()

    assert count == 1


def test_insert_records_logs_duration(temp_db_path, monkeypatch):
    conn = get_conn()
    init_db_schema(conn)
    logs = []

    class ListHandler(logging.Handler):
        def emit(self, record):
            logs.append(record.getMessage())

    handler = ListHandler()
    logger.addHandler(handler)
    monkeypatch.setattr(
        "dashboard_public_health.infrastructure.db.perf_counter", lambda: 1.0
    )

    rec = {
        "country": "UK",
        "year": 2020,
        "disease": "Flu",
        "disease_category": "Infectious",
    }

    insert_records([rec], conn)
    logger.removeHandler(handler)
    conn.close()

    assert any("insert_records" in m and "duration=" in m for m in logs)


def test_crud_round_trip(temp_db_path):
    conn = get_conn()
    init_db_schema(conn)

    rec = HealthRecord(
        country="Japan",
        year=2022,
        disease="Influenza",
        disease_category="Viral",
        prevalence_rate=7.0,
        incidence_rate=4.0,
        mortality_rate=1.1,
        population_affected=5000,
        recovery_rate=92.0,
        dalys=300.0,
        healthcare_access=80.0,
        doctors_per_1000=2.5,
        hospital_beds_per_1000=3.0,
        per_capita_income=35000.0,
        education_index=0.8,
        urbanization_rate=75.0,
        age_group="18-49",
        gender="Female",
        treatment_available="Yes",
        source_file="test.csv",
    )

    new_id = insert_record(rec, conn)
    fetched = get_record_by_id(new_id, conn)
    assert fetched is not None
    assert fetched.country == "Japan"

    updated = update_record_by_id(new_id, {"mortality_rate": 0.9}, conn)
    assert updated == 1
    fetched2 = get_record_by_id(new_id, conn)
    assert fetched2.mortality_rate == 0.9

    deleted = delete_record_by_id(new_id, conn)
    assert deleted == 1
    assert get_record_by_id(new_id, conn) is None

    conn.close()
