from typing import Dict, Any
import pandas as pd
from dashboard_public_health.infrastructure.db import get_conn


def build_where_clause(filters: Dict[str, Any]):
    """
    Convert Python filter parameters into a SQL WHERE clause + parameters.
    Only adds conditions for filters that are not None.
    """

    conditions = []
    params = []

    # Basic filters
    if filters.get("country"):
        conditions.append("country = ?")
        params.append(filters["country"])

    if filters.get("disease"):
        conditions.append("disease = ?")
        params.append(filters["disease"])

    if filters.get("disease_category"):
        conditions.append("disease_category = ?")
        params.append(filters["disease_category"])

    if filters.get("age_group"):
        conditions.append("age_group = ?")
        params.append(filters["age_group"])

    if filters.get("gender"):
        conditions.append("gender = ?")
        params.append(filters["gender"])

    # Year range
    if filters.get("year_from"):
        conditions.append("year >= ?")
        params.append(filters["year_from"])

    if filters.get("year_to"):
        conditions.append("year <= ?")
        params.append(filters["year_to"])

    # Advanced filters: threshold-based
    for adv_key, column in {
        "min_urbanization_rate": "urbanization_rate",
        "min_healthcare_access": "healthcare_access",
        "min_hospital_beds": "hospital_beds_per_1000",
        "min_income": "per_capita_income",
        "min_education": "education_index",
    }.items():
        if filters.get(adv_key) is not None:
            conditions.append(f"{column} >= ?")
            params.append(filters[adv_key])

    # Build final WHERE clause
    where = " AND ".join(conditions)
    if where:
        where = "WHERE " + where

    return where, params


def filter_records_with_connection(**filters) -> pd.DataFrame:
    """
    Execute dynamic SQL query based on provided filters.
    Returns a DataFrame ready for summary/visualization.
    """

    conn = get_conn()

    where, params = build_where_clause(filters)

    query = f"""
        SELECT *
        FROM records
        {where}
    """

    df = pd.read_sql_query(query, conn, params=params)
    return df
