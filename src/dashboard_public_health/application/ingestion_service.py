# application/ingestion_service.py
from dashboard_public_health.infrastructure.csv_reader import load_csv
from dashboard_public_health.infrastructure.db import (
    get_conn,
    init_db_schema,
    insert_records,
)


def ingest_from_csv(csv_path: str) -> None:
    """
    High-level function: CSV -> cleaned DataFrame -> DB
    """
    print(f"[ingestion] Starting ingestion from: {csv_path}")

    # 1. 读原始数据
    raw_df = load_csv(csv_path)

    # # 2. 清洗 + 类型转换
    # cleaned_df = clean_dataframe(raw_df)

    # # 3. 转成 records
    # records = dataframe_to_records(cleaned_df)

    # 4. 建立数据库连接并初始化 schema
    conn = get_conn()
    init_db_schema()

    # 5. 插入数据（避免重复）
    insert_records(raw_df)

    conn.close()
    print("[ingestion] Ingestion completed.")
