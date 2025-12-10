# application/ingestion_service.py
from typing import List, Dict, Any
import pandas as pd
from dashboard_public_health.infrastructure.csv_reader import load_csv
from dashboard_public_health.infrastructure.db import (
    get_conn,
    init_db_schema,
    insert_records,
    drop_all_records,
)
from dashboard_public_health.application.clean import transform_raw_health_csv
from dashboard_public_health.infrastructure.logger import log_action


def dataframe_to_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert a cleaned internal-schema DataFrame into a list of dicts
    ready to be inserted into the database.
    """
    return df.to_dict(orient="records")


@log_action
def ingest_from_csv(csv_path: str) -> None:
    """
    High-level function: CSV -> cleaned DataFrame -> DB
    """
    print(f"[ingestion] Starting ingestion from: {csv_path}")

    # 1. 读原始数据
    raw_df = load_csv(csv_path)

    # 2. 清洗 + 类型转换
    cleaned_df = transform_raw_health_csv(raw_df)

    # 3. 转成 records
    records = dataframe_to_records(cleaned_df)

    # 4. 建立数据库连接并初始化 schema
    conn = get_conn()
    # clear all data
    drop_all_records(conn)

    init_db_schema(conn)

    # 5. 插入数据（避免重复）
    insert_records(records, conn)

    conn.close()
    print("[ingestion] Ingestion completed.")
