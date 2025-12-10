# src/dashboard_public_health/application/clean.py
from __future__ import annotations
import pandas as pd
from dashboard_public_health.application.auto_mapper import auto_match_columns


# -----------------------------------------------------
# 1) Column Normalisation
# -----------------------------------------------------
def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names:
    - lowercase
    - replace spaces with underscores
    - replace / with _
    - replace % with 'percent'
    """
    df = df.copy()
    df.columns = [
        (c.strip().lower().replace(" ", "_").replace("/", "_").replace("%", "percent"))
        for c in df.columns
    ]
    return df


# -----------------------------------------------------
# 2) Internal Schema Mapping
# -----------------------------------------------------
def map_raw_to_internal_schema(
    df_raw: pd.DataFrame, *, source_name: str = "health_csv"
) -> pd.DataFrame:
    """
    Convert raw Global Health Statistics CSV into a unified internal schema.
    This normalises column names, validates required fields, and maps
    heterogeneous CSV structures into a consistent DataFrame.

    Internal schema fields:
        - country
        - year
        - disease
        - disease_category
        - prevalence_rate
        - incidence_rate
        - mortality_rate
        - population_affected
        - recovery_rate
        - dalys
        - healthcare_access
        - doctors_per_1000
        - hospital_beds_per_1000
        - per_capita_income
        - education_index
        - urbanization_rate
        - age_group
        - gender
        - treatment_available
        - source_file
    """

    df = _normalise_columns(df_raw)

    # --- Automatically match fields whenever possible ---
    colmap = auto_match_columns(df)

    # --- Required fields for internal schema ---
    required = [
        "country",
        "year",
        "disease",
        "disease_category",
        "prevalence_ratepercent",
        "incidence_ratepercent",
        "mortality_ratepercent",
        "population_affected",
        "healthcare_accesspercent",
    ]

    missing = [c for c in required if c not in df.columns and c not in colmap]
    if missing:
        raise ValueError(f"Missing required columns for internal schema: {missing}")

    # Use colmap when available; fallback to direct column name
    def pick(col):
        if col in colmap:
            return df[colmap[col]]
        elif col in df.columns:
            return df[col]
        else:
            return None  # optional field missing

    df_internal = pd.DataFrame(
        {
            "country": pick("country"),
            "year": pick("year"),
            "disease": pick("disease"),
            "disease_category": pick("disease_category"),
            "prevalence_rate": pick("prevalence_ratepercent"),
            "incidence_rate": pick("incidence_ratepercent"),
            "mortality_rate": pick("mortality_ratepercent"),
            "population_affected": pick("population_affected"),
            "recovery_rate": pick("recovery_ratepercent"),
            "dalys": pick("dalys"),
            "healthcare_access": pick("healthcare_accesspercent"),
            "doctors_per_1000": pick("doctors_per_1000"),
            "hospital_beds_per_1000": pick("hospital_beds_per_1000"),
            "per_capita_income": pick("per_capita_income_usd"),
            "education_index": pick("education_index"),
            "urbanization_rate": pick("urbanization_ratepercent"),
            "age_group": pick("age_group"),
            "gender": pick("gender"),
            "treatment_available": pick("availability_of_vaccines_treatment"),
        }
    )

    df_internal["source_file"] = source_name
    return df_internal


# -----------------------------------------------------
# 3) Cleaning & Type Conversion
# -----------------------------------------------------
def clean_internal_dataframe(df_internal: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the internal schema DataFrame:
      - convert numeric columns
      - enforce valid year
      - drop rows missing essential fields
      - strip whitespace and normalize string-like columns
    """

    df = df_internal.copy()

    # --- Numeric columns ---
    numeric_cols = [
        "prevalence_rate",
        "incidence_rate",
        "mortality_rate",
        "population_affected",
        "recovery_rate",
        "dalys",
        "healthcare_access",
        "doctors_per_1000",
        "hospital_beds_per_1000",
        "per_capita_income",
        "education_index",
        "urbanization_rate",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Year as integer ---
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # Keep only valid years (optional safety)
    df = df[df["year"].between(1900, 2100, inclusive="both")]

    # --- Drop rows missing critical fields ---
    critical = ["country", "year", "disease"]
    df = df.dropna(subset=critical)

    # --- Clean string fields ---
    str_cols = [
        "country",
        "disease",
        "disease_category",
        "age_group",
        "gender",
        "treatment_available",
    ]

    for col in str_cols:
        if col in df.columns:
            # normalize text for grouping
            df[col] = df[col].astype(str).str.strip().str.replace("  ", " ")

    return df


# -----------------------------------------------------
# 4) Public API (called by ingestion_service)
# -----------------------------------------------------
def transform_raw_health_csv(
    df_raw: pd.DataFrame, *, source_name: str = "health_csv"
) -> pd.DataFrame:
    """
    High-level transformation:
        raw CSV → internal schema → cleaned DataFrame
    """
    df_internal = map_raw_to_internal_schema(df_raw, source_name=source_name)
    df_clean = clean_internal_dataframe(df_internal)
    return df_clean
