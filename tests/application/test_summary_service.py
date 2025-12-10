# tests/application/test_summary_service.py

import pandas as pd
from dashboard_public_health.application.summary_service import (
    compute_policy_summary,
    compute_epidemiology_summary,
    compute_ml_summary,
    compute_global_summary,
)


# Construct minimal sample DF
def sample_df():
    return pd.DataFrame(
        {
            "country": ["A", "A", "B"],
            "year": [2020, 2021, 2020],
            "disease": ["Flu", "Flu", "Covid"],
            "disease_category": ["Inf", "Inf", "Viral"],
            "prevalence_rate": [10, 20, 30],
            "incidence_rate": [5, 6, 7],
            "mortality_rate": [1, 2, 3],
            "population_affected": [1000, 2000, 3000],
            "recovery_rate": [90, 92, 88],
            "dalys": [100, 150, 200],
            "healthcare_access": [70, 75, 80],
            "doctors_per_1000": [3, 4, 5],
            "hospital_beds_per_1000": [2, 3, 4],
            "per_capita_income": [30000, 32000, 15000],
            "education_index": [0.8, 0.82, 0.6],
            "urbanization_rate": [60, 65, 40],
            "age_group": ["18-49", "50-64", "18-49"],
            "gender": ["Both", "Male", "Female"],
            "treatment_available": ["Yes", "Yes", "No"],
        }
    )


def test_policy_summary():
    df = sample_df()
    summary = compute_policy_summary(df)
    assert "avg_prevalence" in summary
    assert "highest_prevalence_country" in summary


def test_epidemiology_summary():
    df = sample_df()
    summary = compute_epidemiology_summary(df)
    assert "yearly_trend" in summary
    assert "correlations" in summary


def test_ml_summary():
    df = sample_df()
    summary = compute_ml_summary(df)
    assert "missing_values" in summary
    assert "feature_stats" in summary
    assert "outlier_thresholds" in summary


def test_global_summary():
    df = sample_df()
    summary = compute_global_summary(df)
    assert "top_mortality_countries" in summary
    assert "disease_burden" in summary
