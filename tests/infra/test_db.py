# tests/infra/test_db.py
from dashboard_public_health.infrastructure.db import (
    get_conn,
    init_db_schema,
    insert_records,
)
from dashboard_public_health.domain.models import HealthRecord


# -------------------------------------------------------------
# 1. 测试 DB Schema 是否被正确创建
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
# 2. 测试 INSERT + UNIQUE 去重 逻辑
# -------------------------------------------------------------
def test_insert_records_inserts_and_ignores_duplicates(temp_db_path):
    conn = get_conn()
    init_db_schema(conn)

    # ⚠️ 按新 internal schema 构造一条合法记录
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

    # 去重后应该只剩 1 条
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
