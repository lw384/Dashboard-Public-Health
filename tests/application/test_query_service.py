# tests/application/test_exploration_service.py
import pandas as pd

from dashboard_public_health.infrastructure.db import (
    get_conn,
    init_db_schema,
    insert_records,
)
from dashboard_public_health.application.query_service import filter_records


def _seed_sample_data(conn):
    """
    往临时 DB 里插入几条示例数据，用来测试 filter 逻辑。
    """
    init_db_schema(conn)

    records = [
        {
            "date": "2020-01-01",
            "country": "UK",
            "indicator": "daily_new_cases",
            "value": 10.0,
            "age_group": "18-49",
            "source_file": "test.csv",
        },
        {
            "date": "2020-01-02",
            "country": "UK",
            "indicator": "daily_new_cases",
            "value": 20.0,
            "age_group": "50-64",
            "source_file": "test.csv",
        },
        {
            "date": "2020-01-01",
            "country": "US",
            "indicator": "daily_new_cases",
            "value": 5.0,
            "age_group": "18-49",
            "source_file": "test.csv",
        },
        {
            "date": "2020-02-01",
            "country": "UK",
            "indicator": "vaccination_rate",
            "value": 0.8,
            "age_group": "18-49",
            "source_file": "test.csv",
        },
    ]

    insert_records(records, conn=conn)


def test_filter_records_no_filters_returns_all(temp_db_path):
    conn = get_conn()
    _seed_sample_data(conn)

    df = filter_records(conn)

    # 一共插入了 4 条记录
    assert len(df) == 4
    # 列名检查
    assert set(df.columns) == {
        "date",
        "country",
        "indicator",
        "value",
        "age_group",
        "source_file",
    }

    conn.close()


def test_filter_records_by_country(temp_db_path):
    conn = get_conn()
    _seed_sample_data(conn)

    df_uk = filter_records(conn, country="UK")
    df_us = filter_records(conn, country="US")

    assert len(df_uk) == 3
    assert set(df_uk["country"]) == {"UK"}

    assert len(df_us) == 1
    assert set(df_us["country"]) == {"US"}

    conn.close()


def test_filter_records_by_date_range(temp_db_path):
    conn = get_conn()
    _seed_sample_data(conn)

    # 只取 2020-01-01 到 2020-01-31
    df_jan = filter_records(conn, start_date="2020-01-01", end_date="2020-01-31")

    # 预期保留前三条，丢掉 2020-02-01
    assert len(df_jan) == 3
    assert df_jan["date"].max() <= "2020-01-31"

    conn.close()


def test_filter_records_by_age_group_and_indicator(temp_db_path):
    conn = get_conn()
    _seed_sample_data(conn)

    df_18_49_cases = filter_records(
        conn,
        age_group="18-49",
        indicator="daily_new_cases",
    )

    # 18-49 + daily_new_cases 对应两条记录 (UK + US)
    assert len(df_18_49_cases) == 2
    assert set(df_18_49_cases["age_group"]) == {"18-49"}
    assert set(df_18_49_cases["indicator"]) == {"daily_new_cases"}

    conn.close()
