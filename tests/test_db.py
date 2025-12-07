from dashboard_public_health.infrastructure.db import (
    get_conn,
    init_db_schema,
    insert_records,
)


def test_init_db_creates_table(temp_db_path):
    # temp_db_path fixture 已经 monkeypatch 了 config.DB_PATH
    conn = get_conn()
    init_db_schema()

    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='record';"
    )
    row = cursor.fetchone()

    assert row is not None
    conn.close()


def test_insert_records_inserts_and_ignores_duplicates(temp_db_path):
    # temp_db_path fixture 确保 config.DB_PATH 已经指向一个空白的临时 DB
    conn = get_conn()
    init_db_schema(conn)

    records = [
        {
            "date": "2020-01-01",
            "country": "UK",
            "indicator": "VACCINATION_RATE",
            "value": 50.0,
            "age_group": "18-25",
            "source_file": "test.csv",
        },
        {
            "date": "2020-01-01",
            "country": "UK",
            "indicator": "VACCINATION_RATE",
            "value": 50.0,
            "age_group": "18-25",
            "source_file": "test.csv",
        },  # duplicate
    ]

    # ⚠️ 一定是 records 在前，conn 在后
    insert_records(records, conn=conn)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM record;")
    (count,) = cursor.fetchone()

    # 临时 DB 最开始是空的，只插入这两条 → 去重后应该只留 1 条
    assert count == 1

    conn.close()
