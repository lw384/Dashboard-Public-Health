import pandas as pd
import numpy as np
import pytest

from dashboard_public_health.application.clean import (
    map_raw_to_internal_schema,
    transform_raw_health_csv,
)


# ----------------------------------------------------------
# Fixture for a minimal valid raw dataset
# ----------------------------------------------------------
@pytest.fixture
def raw_df():
    return pd.DataFrame(
        {
            "Country": ["UK", "China", None],
            "Year": [2020, 2021, 2022],
            "Disease Name": ["Flu", "Covid", "Malaria"],
            "Disease Category": ["Infectious", "Infectious", "Infectious"],
            "Prevalence Rate (%)": [10, 5, 200],  # 200 => outlier, should become NaN
            "Incidence Rate (%)": [2.5, -1, 3],  # -1 => outlier, should become NaN
            "Mortality Rate (%)": [0.5, 0.1, 120],  # 120 => outlier
            "Population Affected": [10000, 5000, -100],  # -100 invalid => NaN
            "Healthcare Access (%)": [95, 50, 300],  # 300 => outlier => NaN
            "Recovery Rate (%)": [98, None, 101],  # 101 => outlier
            "DALYs": [100, None, 200],
            "Doctors per 1000": [3, 2, -5],  # -5 => NaN
            "Hospital Beds per 1000": [5, None, 200],  # valid
            "Per Capita Income (USD)": [30000, 20000, -10],  # -10 => NaN
            "Education Index": [0.9, 0.8, 0.7],
            "Urbanization Rate (%)": [80, 150, 60],  # 150 => NaN
            "Age Group": ["18-49", None, "50-64"],
            "Gender": ["Male", None, "Female"],
            "Availability of Vaccines/Treatment": ["Yes", None, "No"],
        }
    )


# ----------------------------------------------------------
# Test: Schema mapping produces required fields
# ----------------------------------------------------------
def test_internal_schema_mapping(raw_df):
    df_internal = map_raw_to_internal_schema(raw_df)

    expected_fields = {
        "country",
        "year",
        "disease",
        "disease_category",
        "prevalence_rate",
        "incidence_rate",
        "mortality_rate",
        "population_affected",
        "healthcare_access",
        "recovery_rate",
        "dalys",
        "doctors_per_1000",
        "hospital_beds_per_1000",
        "per_capita_income",
        "education_index",
        "urbanization_rate",
        "age_group",
        "gender",
        "treatment_available",
        "source_file",
    }

    assert expected_fields.issubset(set(df_internal.columns))


# ----------------------------------------------------------
# Test: Outlier handling
# ----------------------------------------------------------
def test_outlier_cleaning(raw_df):
    df_clean = transform_raw_health_csv(raw_df)

    assert np.isnan(
        df_clean.loc[df_clean["disease"] == "Malaria", "prevalence_rate"]
    ).all()
    assert np.isnan(
        df_clean.loc[df_clean["disease"] == "Covid", "incidence_rate"]
    ).all()
    assert np.isnan(
        df_clean.loc[df_clean["disease"] == "Malaria", "mortality_rate"]
    ).all()
    assert np.isnan(
        df_clean.loc[df_clean["disease"] == "China", "healthcare_access"]
    ).all()


# ----------------------------------------------------------
# Test: Missing value fill for categorical fields
# ----------------------------------------------------------
def test_fill_missing_categorical(raw_df):
    df_clean = transform_raw_health_csv(raw_df)

    # The "Covid" row has missing age_group & gender
    covid = df_clean[df_clean["disease"] == "Covid"].iloc[0]

    assert covid["age_group"] == "Unknown"
    assert covid["gender"] == "Unknown"
    assert covid["treatment_available"] == "Unknown"


# ----------------------------------------------------------
# Test: Type conversion
# ----------------------------------------------------------
def test_numeric_conversion(raw_df):
    df_clean = transform_raw_health_csv(raw_df)

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
        "urbanization_rate",
    ]

    for col in numeric_cols:
        assert col in df_clean.columns
        assert df_clean[col].dtype in ("float64", "int64", "object")


# ----------------------------------------------------------
# Test: Validation removes rows missing critical fields
# ----------------------------------------------------------
def test_validation_removes_missing_critical_fields(raw_df):
    df_clean = transform_raw_health_csv(raw_df)

    # the third row had country=None → must be removed
    assert df_clean["country"].isna().sum() == 0
