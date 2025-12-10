import pandas as pd
import pytest

from dashboard_public_health.application.summary_service import (
    descriptive_summary,
    time_trend_summary,
    grouped_summary,
    correlation_summary,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "country": ["A", "A", "B", "B"],
            "year": [2000, 2001, 2000, 2001],
            "prevalence_rate": [10, 12, 8, 9],
            "incidence_rate": [5, 6, 4, 5],
            "mortality_rate": [2, 3, 1, 2],
            "urbanization_rate": [50, 60, 55, 65],
            "per_capita_income": [30000, 31000, 20000, 22000],
            "education_index": [0.8, 0.85, 0.7, 0.72],
        }
    )


# ---------------------------------------------------------
# 1. Test descriptive summary
# ---------------------------------------------------------
def test_descriptive_summary(sample_df):
    output = descriptive_summary(sample_df)

    assert isinstance(output, str)
    assert "📊 Basic Statistics" in output
    assert "- prevalence_rate:" in output
    assert "mean=" in output
    assert "min=" in output
    assert "max=" in output


# ---------------------------------------------------------
# 2. Test time trend summary
# ---------------------------------------------------------
def test_time_trend_summary(sample_df):
    output = time_trend_summary(sample_df)

    assert isinstance(output, str)
    assert "📈 Trends Over Time" in output
    assert "Year   Prev   Inc   Mort" in output
    assert "2000" in output
    assert "2001" in output


# ---------------------------------------------------------
# 3. Test grouped summary
# ---------------------------------------------------------
def test_grouped_summary(sample_df):
    output = grouped_summary(sample_df, "country")

    assert isinstance(output, str)
    assert "📚 Grouped by country" in output
    assert "A" in output
    assert "B" in output
    assert "Prev" in output


# ---------------------------------------------------------
# 4. Test correlation summary
# ---------------------------------------------------------
def test_correlation_summary(sample_df):
    output = correlation_summary(sample_df)

    assert isinstance(output, str)
    assert "🔗 Correlation Matrix" in output

    # Key expected pairs
    assert "prevalence_rate ↔ mortality_rate" in output
    assert "prevalence_rate ↔ urbanization_rate" in output
