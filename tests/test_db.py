from dashboard_public_health.infrastructure.db import (
    get_conn,
    init_db_schema,
    insert_records,
)
from dashboard_public_health import config


def test_init_db_creates_table(temp_db_path):
    # temp_db_path fixture 已经 monkeypatch 了 config.DB_PATH
    conn = get_conn()
    init_db_schema()

    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='public_health_records';"
    )
    row = cursor.fetchone()
    assert row is not None
    conn.close()


def test_insert_records_inserts_and_ignores_duplicates(temp_db_path):
    conn = get_conn()
    init_db_schema()

    records = [
        {
            "date": "2020-01-01",
            "country": "UK",
            "indicator": "VACCINATION_RATE",
            "value": 50.0,
            "age_group": "18-25",
        },
        {
            "date": "2020-01-01",
            "country": "UK",
            "indicator": "VACCINATION_RATE",
            "value": 50.0,
            "age_group": "18-25",
        },  # duplicate
    ]

    insert_records(records)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM public_health_records;")
    (count,) = cursor.fetchone()
    # 如果 UNIQUE(date, country, indicator, age_group) 正常工作，应该只插入一条
    assert count == 1
    conn.close()
