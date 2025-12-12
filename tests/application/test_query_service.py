import pytest
import pandas as pd
import sqlite3
from dataclasses import asdict

from dashboard_public_health.application.query_service import (
    build_where_clause,
    filter_records_with_connection,
)
from dashboard_public_health.infrastructure.db import get_conn
from dashboard_public_health.ui.cli.helpers import collect_filters
from dashboard_public_health.domain.models import FilterCriteria


# --------------------------------------------------------------
# Fixture: temporary DB with minimal sample data
# --------------------------------------------------------------
@pytest.fixture
def sample_db(temp_db_path):
    """
    Creates a temporary SQLite DB with a minimal 'records' table
    and a few rows for filtering tests.
    """

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT,
            year INTEGER,
            disease TEXT,
            disease_category TEXT,
            prevalence_rate REAL,
            incidence_rate REAL,
            mortality_rate REAL,
            population_affected REAL,
            recovery_rate REAL,
            dalys REAL,
            healthcare_access REAL,
            doctors_per_1000 REAL,
            hospital_beds_per_1000 REAL,
            per_capita_income REAL,
            education_index REAL,
            urbanization_rate REAL,
            age_group TEXT,
            gender TEXT,
            treatment_available TEXT,
            source_file TEXT
        )
        """
    )

    sample_rows = [
        (
            "Italy",
            2020,
            "Influenza",
            "Viral",
            10.5,
            7.2,
            5.1,
            100000,
            85.0,
            1200,
            70.0,
            3.5,
            5.0,
            45000,
            0.75,
            80.0,
            "18-49",
            "Male",
            "Yes",
            "test.csv",
        ),
        (
            "France",
            2021,
            "COVID-19",
            "Viral",
            15.0,
            9.4,
            7.0,
            200000,
            90.0,
            2500,
            78.0,
            4.0,
            6.0,
            52000,
            0.82,
            85.0,
            "50-64",
            "Female",
            "Yes",
            "test.csv",
        ),
    ]

    cur.executemany(
        """
        INSERT INTO records (
            country, year, disease, disease_category, prevalence_rate,
            incidence_rate, mortality_rate, population_affected,
            recovery_rate, dalys, healthcare_access,
            doctors_per_1000, hospital_beds_per_1000,
            per_capita_income, education_index, urbanization_rate,
            age_group, gender, treatment_available, source_file
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_rows,
    )

    conn.commit()
    conn.close()


# --------------------------------------------------------------
# Tests for build_where_clause
# --------------------------------------------------------------


def test_build_where_clause_basic():
    filters = {"country": "Italy", "disease": "Influenza"}
    where, params = build_where_clause(filters)

    assert "country = ?" in where
    assert "disease = ?" in where
    assert params == ["Italy", "Influenza"]


def test_build_where_clause_year_range():
    filters = {"year_from": 2019, "year_to": 2021}
    where, params = build_where_clause(filters)

    assert "year >= ?" in where
    assert "year <= ?" in where
    assert params == [2019, 2021]


def test_build_where_clause_advanced_filters():
    filters = {"min_income": 50000}
    where, params = build_where_clause(filters)

    assert "per_capita_income >= ?" in where
    assert params == [50000]


def test_build_where_clause_ignores_empty_values():
    filters = {"country": None, "disease": "", "year_from": None}
    where, params = build_where_clause(filters)

    assert where == ""
    assert params == []


def test_build_where_clause_all_supported_fields():
    filters = {
        "country": "France",
        "disease": "COVID-19",
        "disease_category": "Viral",
        "age_group": "50-64",
        "gender": "Female",
        "year_from": 2020,
        "year_to": 2022,
        "min_urbanization_rate": 80,
        "min_healthcare_access": 70,
        "min_hospital_beds": 4,
        "min_income": 40000,
        "min_education": 0.5,
    }

    where, params = build_where_clause(filters)

    # All conditions should be present and ordered with params
    for snippet in [
        "country = ?",
        "disease = ?",
        "disease_category = ?",
        "age_group = ?",
        "gender = ?",
        "year >= ?",
        "year <= ?",
        "urbanization_rate >= ?",
        "healthcare_access >= ?",
        "hospital_beds_per_1000 >= ?",
        "per_capita_income >= ?",
        "education_index >= ?",
    ]:
        assert snippet in where

    assert params == [
        "France",
        "COVID-19",
        "Viral",
        "50-64",
        "Female",
        2020,
        2022,
        80,
        70,
        4,
        40000,
        0.5,
    ]


# --------------------------------------------------------------
# Tests for filter_records_with_connection
# --------------------------------------------------------------


def test_filter_country(sample_db):
    df = filter_records_with_connection(country="Italy")

    assert not df.empty
    assert all(df["country"] == "Italy")
    assert len(df) == 1  # Only Italy row


def test_filter_disease(sample_db):
    df = filter_records_with_connection(disease="COVID-19")

    assert len(df) == 1
    assert df.iloc[0]["disease"] == "COVID-19"


def test_filter_year_range(sample_db):
    df = filter_records_with_connection(year_from=2020, year_to=2020)

    assert len(df) == 1
    assert df.iloc[0]["year"] == 2020


def test_filter_advanced_income(sample_db):
    df = filter_records_with_connection(min_income=50000)

    # Only France row has income >= 52000
    assert len(df) == 1
    assert df.iloc[0]["country"] == "France"


def test_filter_multiple_conditions(sample_db):
    df = filter_records_with_connection(
        disease_category="Viral",
        gender="Female",
    )

    assert len(df) == 1
    assert df.iloc[0]["country"] == "France"


def test_filter_advanced_combination(sample_db):
    df = filter_records_with_connection(
        min_healthcare_access=75,
        min_income=48000,
    )

    # Only France matches both thresholds in sample data
    assert len(df) == 1
    assert df.iloc[0]["country"] == "France"


# --------------------------------------------------------------
# Tests for shared filter collector + integration
# --------------------------------------------------------------


def _input_sequence(values):
    """Helper to simulate user input sequence."""
    it = iter(values)

    def _reader(_prompt=""):
        return next(it, "")

    return _reader


def test_collect_filters_returns_full_schema():
    reader = _input_sequence([""] * 12)
    filters = collect_filters(input_func=reader, defaults=None)

    expected_keys = {
        "country",
        "disease",
        "disease_category",
        "age_group",
        "gender",
        "year_from",
        "year_to",
        "min_urbanization_rate",
        "min_healthcare_access",
        "min_hospital_beds",
        "min_income",
        "min_education",
    }

    data = asdict(filters)
    assert set(data.keys()) == expected_keys
    assert all(v is None for v in data.values())


def test_collect_filters_applies_defaults():
    defaults = {"country": "Italy", "min_income": 50000, "year_from": 2020}
    reader = _input_sequence(["", "", "", "", "", "", "", "", "", "", "", ""])

    filters = collect_filters(input_func=reader, defaults=defaults)

    assert filters.country == "Italy"
    assert filters.min_income == 50000
    assert filters.year_from == 2020


def test_build_where_clause_matches_shared_keys():
    reader = _input_sequence(
        [
            "France",  # country
            "COVID-19",  # disease
            "Viral",  # disease_category
            "50-64",  # age_group
            "Female",  # gender
            "2020",  # year_from
            "2022",  # year_to
            "80",  # min_urbanization_rate
            "70",  # min_healthcare_access
            "4",  # min_hospital_beds
            "40000",  # min_income
            "0.5",  # min_education
        ]
    )

    filters = collect_filters(input_func=reader, defaults=None)
    where, params = build_where_clause(filters)

    assert "country = ?" in where
    assert "disease = ?" in where
    assert "disease_category = ?" in where
    assert "age_group = ?" in where
    assert "gender = ?" in where
    assert "year >= ?" in where and "year <= ?" in where
    assert "urbanization_rate >= ?" in where
    assert "healthcare_access >= ?" in where
    assert "hospital_beds_per_1000 >= ?" in where
    assert "per_capita_income >= ?" in where
    assert "education_index >= ?" in where

    assert params == [
        "France",
        "COVID-19",
        "Viral",
        "50-64",
        "Female",
        2020,
        2022,
        80.0,
        70.0,
        4.0,
        40000.0,
        0.5,
    ]


def test_build_where_clause_accepts_filtercriteria():
    criteria = FilterCriteria(
        country="Italy",
        disease="Influenza",
        year_from=2019,
        year_to=2021,
    )

    where, params = build_where_clause(criteria)

    assert "country = ?" in where
    assert "disease = ?" in where
    assert "year >= ?" in where and "year <= ?" in where
    assert params == ["Italy", "Influenza", 2019, 2021]


def test_filter_records_with_filtercriteria(sample_db):
    criteria = FilterCriteria(country="France", disease_category="Viral")
    df = filter_records_with_connection(criteria)

    assert len(df) == 1
    assert df.iloc[0]["country"] == "France"


def test_filter_records_as_models(sample_db):
    criteria = FilterCriteria(country="France")
    records = filter_records_with_connection(criteria, as_records=True)

    assert len(records) == 1
    assert records[0].country == "France"
    assert records[0].disease == "COVID-19"
