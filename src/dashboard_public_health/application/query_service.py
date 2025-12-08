from __future__ import annotations
from typing import Optional
import pandas as pd
from dashboard_public_health.infrastructure.db import get_conn
from dashboard_public_health.infrastructure.db import fetch_all_records
from dashboard_public_health.domain.models import FilterCriteria
from dashboard_public_health.domain.rules import (
    apply_filter,
)
from dashboard_public_health.domain.analysis import (
    calculate_summary,
    group_by_country,
)


def filter_records(
    conn,
    *,
    country: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    age_group: Optional[str] = None,
    indicator: Optional[str] = None,
) -> pd.DataFrame:
    """
    Query records from the 'record' table with optional filters.

    Args:
        conn: An open sqlite3.Connection.
        country: Exact country match (e.g. 'Urban', 'UK').
        start_date: Inclusive start date, format 'YYYY-MM-DD'.
        end_date: Inclusive end date, format 'YYYY-MM-DD'.
        age_group: Exact age group (e.g. '0-17', '18-49', 'Unknown').
        indicator: Indicator name (e.g. 'daily_new_cases').

    Returns:
        A pandas DataFrame with columns:
        [date, country, indicator, value, age_group, source_file]
    """
    where_clauses = []
    params: list = []

    if country:
        where_clauses.append("country = ?")
        params.append(country)

    if start_date:
        where_clauses.append("date >= ?")
        params.append(start_date)

    if end_date:
        where_clauses.append("date <= ?")
        params.append(end_date)

    if age_group:
        where_clauses.append("age_group = ?")
        params.append(age_group)

    if indicator:
        where_clauses.append("indicator = ?")
        params.append(indicator)

    base_sql = """
        SELECT
            date,
            country,
            indicator,
            value,
            age_group,
            source_file
        FROM record
    """

    if where_clauses:
        base_sql += " WHERE " + " AND ".join(where_clauses)

    base_sql += " ORDER BY date;"

    df = pd.read_sql_query(base_sql, conn, params=params)

    return df


def filter_records_with_connection(
    *,
    country: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    age_group: Optional[str] = None,
    indicator: Optional[str] = None,
) -> pd.DataFrame:
    """
    Convenience wrapper that opens/closes the DB connection internally.
    Suitable for use from the CLI layer.
    """
    conn = get_conn()
    try:
        df = filter_records(
            conn,
            country=country,
            start_date=start_date,
            end_date=end_date,
            age_group=age_group,
            indicator=indicator,
        )
    finally:
        conn.close()

    return df


def summarise_df(df: pd.DataFrame) -> dict:
    """
    Compute basic summary statistics on a filtered DataFrame.

    Returns:
        A dictionary with:
            - record_count
            - min_value
            - max_value
            - mean_value
            - start_date
            - end_date
    """
    if df.empty:
        return {
            "record_count": 0,
            "min_value": None,
            "max_value": None,
            "mean_value": None,
            "start_date": None,
            "end_date": None,
        }

    return {
        "record_count": len(df),
        "min_value": df["value"].min(),
        "max_value": df["value"].max(),
        "mean_value": round(df["value"].mean(), 2),
        "start_date": df["date"].min(),
        "end_date": df["date"].max(),
    }


def summarise_filtered_data(
    *,
    country=None,
    start_date=None,
    end_date=None,
    age_group=None,
    indicator=None,
):
    conn = get_conn()

    try:
        df = filter_records(
            conn,
            country=country,
            start_date=start_date,
            end_date=end_date,
            age_group=age_group,
            indicator=indicator,
        )
    finally:
        conn.close()

    return summarise_df(df)
