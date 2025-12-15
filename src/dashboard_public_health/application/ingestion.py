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
from dashboard_public_health.domain.models import HealthRecord
from dashboard_public_health.application.clean import transform_raw_health_csv
from dashboard_public_health.infrastructure.logger import log_action


def dataframe_to_records(df: pd.DataFrame) -> List[HealthRecord]:
    """
    Convert a cleaned internal-schema DataFrame into a list of HealthRecord
    ready to be inserted into the database.
    """
    return [HealthRecord.from_dict(rec) for rec in df.to_dict(orient="records")]


@log_action
def ingest_from_csv(csv_path: str) -> None:
    """
    High-level function: CSV -> cleaned DataFrame -> DB
    """
    print(f"[ingestion] Starting ingestion from: {csv_path}")

    # 1. Load raw data
    raw_df = load_csv(csv_path)

    # 2. Clean + type conversion
    cleaned_df = transform_raw_health_csv(raw_df)

    # 3. Convert to records
    records = dataframe_to_records(cleaned_df)

    # 4. Open DB connection and init schema
    conn = get_conn()
    init_db_schema(conn)
    # clear all data after schema exists
    drop_all_records(conn)

    # 5. Insert data (deduplicated)
    insert_records(records, conn)

    conn.close()
    print("[ingestion] Ingestion completed.")
