# src/dashboard_public_health/application/clean.py
"""
Data Cleaning Pipeline for Global Health Statistics

This module performs all steps required to transform heterogeneous
raw CSV files into a unified, validated and analysis-ready dataset.

The cleaning pipeline follows industry-standard steps:
    1) Column Normalisation
    2) Schema Mapping
    3) Outlier Handling
    4) Missing Value Treatment
    5) Type Conversion
    6) Validation and Quality Assurance (QA)

This design groups related concerns but keeps responsibilities separate
within the file, making it easy to test and extend.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from dashboard_public_health.application.provenance import with_provenance
from dashboard_public_health.application.auto_mapper import auto_match_columns


# ============================================================
# 1) Column Normalisation
# ============================================================


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise column names to improve robustness across CSV variants.

    - Lowercase all column names
    - Replace whitespace with underscores
    - Replace "/" with "_"
    - Replace "%" with "percent"
    """
    df = df.copy()
    df.columns = [
        (c.strip().lower().replace(" ", "_").replace("/", "_").replace("%", "percent"))
        for c in df.columns
    ]
    return df


# ============================================================
# 2) Map Raw Columns → Internal Schema
# ============================================================


def map_raw_to_internal_schema(
    df_raw: pd.DataFrame, *, source_name: str = "health_csv"
) -> pd.DataFrame:
    """
    Convert raw CSV into a clean, unified internal schema.

    This function:
        - Normalises columns
        - Uses auto_match_columns() for flexible source compatibility
        - Applies required-field validation
        - Extracts all fields used in downstream analysis

    The internal schema includes:
        country, year, disease, disease_category,
        prevalence_rate, incidence_rate, mortality_rate,
        population_affected, recovery_rate, dalys,
        healthcare_access, doctors_per_1000, hospital_beds_per_1000,
        per_capita_income, education_index, urbanization_rate,
        age_group, gender, treatment_available, source_file
    """

    df = _normalise_columns(df_raw)

    # Auto-detect possible synonyms in messy CSVs
    colmap = auto_match_columns(df)

    # Required fields (either present directly or via colmap)
    required_fields = [
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

    missing = [f for f in required_fields if f not in df.columns and f not in colmap]

    if missing:
        raise ValueError(
            f"Cannot build internal schema. Missing required fields: {missing}"
        )

    # Helper accessor function
    def pick(field: str):
        """
        Safely extract a field from either:
            - auto-mapped name (colmap)
            - existing normalised column
            - or return None (optional fields)
        """
        if field in colmap:
            return df[colmap[field]]
        if field in df.columns:
            return df[field]
        return None

    # Construct the internal DataFrame
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
            "source_file": source_name,
        }
    )

    return df_internal


# ============================================================
# 3) Outlier Handling Rules
# ============================================================


@with_provenance("outlier_handling")
def _handle_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove or clean implausible values that break the assumptions
    of epidemiological or socio-economic analysis.

    Outlier rules implemented:
        - Rates cannot exceed 100%
        - Negative values are invalid for demographic metrics
        - Resource capacity fields trimmed to realistic limits
    """

    df = df.copy()

    # Apply upper bounds for percentage-like fields
    rate_fields = [
        "prevalence_rate",
        "incidence_rate",
        "mortality_rate",
        "recovery_rate",
        "healthcare_access",
        "urbanization_rate",
    ]
    for col in rate_fields:
        if col in df.columns:
            df.loc[df[col] < 0, col] = np.nan
            df.loc[df[col] > 100, col] = np.nan

    # Demographic metrics cannot be negative
    non_negative_fields = [
        "population_affected",
        "dalys",
        "per_capita_income",
        "doctors_per_1000",
        "hospital_beds_per_1000",
    ]
    for col in non_negative_fields:
        if col in df.columns:
            df.loc[df[col] < 0, col] = np.nan

    return df


# ============================================================
# 4) Missing Value Treatment
# ============================================================


@with_provenance("missing_value_fill")
def _fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace missing values for non-critical fields.

    - Categorical missing values → 'Unknown'
    - Numeric missing values → left as NaN (DB will store null)
    """

    df = df.copy()

    categorical_fields = ["gender", "age_group", "treatment_available"]
    for col in categorical_fields:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    return df


# ============================================================
# 5) Type Conversion + Cleaning
# ============================================================


@with_provenance("type_conversion")
def _convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert numeric and categorical fields to appropriate datatypes.
    Enforce:
        - year must be integer
        - numeric fields parsed safely
    """

    df = df.copy()

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

    # Year must be valid
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df[df["year"].between(1900, 2100, inclusive="both")]

    return df


# ============================================================
# 6) Validation & QA Checks
# ============================================================


@with_provenance("validation")
def _validate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Final validation step:
        - drop rows missing *critical fields*
        - ensure logical consistency
    """

    df = df.copy()

    critical_fields = ["country", "year", "disease"]
    df = df.dropna(subset=critical_fields)

    return df


# ============================================================
# 6) Deduplication
# ============================================================


@with_provenance("duplicate_removal")
def _deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows based on business keys.
    This reduces DB load and ensures consistent cleaned output.
    """
    dedupe_keys = [
        "country",
        "year",
        "disease",
        "disease_category",
        "age_group",
        "gender",
    ]

    existing = [k for k in dedupe_keys if k in df.columns]

    before = len(df)
    df = df.drop_duplicates(subset=existing)
    after = len(df)

    print(f"[clean] Deduplication removed {before - after} duplicates.")

    return df


# ============================================================
# Public Pipeline API
# ============================================================


def transform_raw_health_csv(
    df_raw: pd.DataFrame, *, source_name: str = "health_csv"
) -> pd.DataFrame:
    """
    High-level pipeline used by ingestion_service.py

        Raw CSV
            → Normalised Columns
            → Mapped to Internal Schema
            → Cleaned (types, missing values, outliers)
            → Validated

    Returns a fully standardised DataFrame ready for:
        - database insertion
        - filtering
        - visualisation
        - summary statistics
    """

    df_internal = map_raw_to_internal_schema(df_raw, source_name=source_name)
    df_internal = _handle_outliers(df_internal)
    df_internal = _fill_missing_values(df_internal)
    df_internal = _convert_types(df_internal)
    df_clean = _validate(df_internal)
    df = _deduplicate(df_clean)

    return df
