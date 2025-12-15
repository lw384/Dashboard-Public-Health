from typing import Dict, Any, Optional, List
import pandas as pd
from dashboard_public_health.infrastructure.db import get_conn
from dashboard_public_health.infrastructure.logger import log_action, logger
from dashboard_public_health.domain.models import FilterCriteria, HealthRecord
from time import perf_counter


def _normalize_filters(filters: Optional[FilterCriteria | Dict[str, Any]] = None, **kwargs):
    """
    Accept either a FilterCriteria dataclass, a dict, or kwargs and return a dict.
    """
    if filters is None:
        return {k: v for k, v in kwargs.items()}

    if isinstance(filters, FilterCriteria):
        return filters.__dict__.copy()

    # assume mapping
    return dict(filters)


def build_where_clause(filters: FilterCriteria | Dict[str, Any]):
    """
    Convert Python filter parameters into a SQL WHERE clause + parameters.
    Only adds conditions for filters that are not None.
    """

    filters = _normalize_filters(filters)
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


@log_action
def filter_records_with_connection(
    filters: Optional[FilterCriteria | Dict[str, Any]] = None,
    *,
    as_records: bool = False,
    **filters_kwargs,
) -> pd.DataFrame | List[HealthRecord]:
    """
    Execute dynamic SQL query based on provided filters.
    Returns a DataFrame by default, or list[HealthRecord] when as_records=True.
    """

    conn = get_conn()

    merged_filters = _normalize_filters(filters, **filters_kwargs)
    where, params = build_where_clause(merged_filters)

    query = f"""
        SELECT *
        FROM records
        {where}
    """

    start = perf_counter()
    df = pd.read_sql_query(query, conn, params=params)
    duration = perf_counter() - start
    logger.info(f"[perf] filter_records_with_connection duration={duration:.4f}s rows={len(df)}")
    if as_records:
        return [HealthRecord.from_dict(rec) for rec in df.to_dict(orient="records")]
    return df
