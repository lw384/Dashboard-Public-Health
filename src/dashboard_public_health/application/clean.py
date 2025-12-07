# src/public_health_insights/application/ingestion_service.py
from typing import List, Dict, Any

import pandas as pd

from dashboard_public_health.infrastructure.csv_reader import load_csv
from dashboard_public_health.infrastructure.db import (
    get_conn,
    init_db,
    save_records,
)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply basic cleaning & type conversion.
    Adjust the column names to match your dataset.
    """

    # 1. 统一列名（根据你的实际 CSV 改）
    # 假设原始列为 ['Date', 'Country', 'Indicator', 'Value', 'AgeGroup']
    df = df.rename(
        columns={
            "Date": "date",
            "Country": "country",
            "Indicator": "indicator",
            "Value": "value",
            "AgeGroup": "age_group",
        }
    )

    # 2. 处理缺失值（示例策略）
    #   - country / indicator 缺失行直接丢弃
    df = df.dropna(subset=["date", "country", "indicator", "value"])

    #   - age_group 为空填 Unknown
    df["age_group"] = df["age_group"].fillna("Unknown")

    # 3. 类型转换
    # date → datetime 再转回 ISO 字符串，方便存 SQLite
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])  # 无法解析日期的行丢弃
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # value → float
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    # 4. 去掉前后空格，统一格式
    df["country"] = df["country"].astype(str).str.strip()
    df["indicator"] = df["indicator"].astype(str).str.strip()
    df["age_group"] = df["age_group"].astype(str).str.strip()

    print(f"[ingestion] Cleaned dataframe has {len(df)} rows.")
    return df


def dataframe_to_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert the cleaned DataFrame into a list of dicts
    so it can be inserted into the database layer.
    """
    records: List[Dict[str, Any]] = df.to_dict(orient="records")
    return records


def ingest_from_csv(csv_path: str) -> None:
    """
    High-level function: CSV -> cleaned DataFrame -> DB
    """
    print(f"[ingestion] Starting ingestion from: {csv_path}")

    # 1. 读原始数据
    raw_df = load_csv(csv_path)

    # 2. 清洗 + 类型转换
    cleaned_df = clean_dataframe(raw_df)

    # 3. 转成 records
    records = dataframe_to_records(cleaned_df)

    # 4. 建立数据库连接并初始化 schema
    conn = get_conn()
    init_db(conn)

    # 5. 插入数据（避免重复）
    save_records(conn, records)

    conn.close()
    print("[ingestion] Ingestion completed.")
