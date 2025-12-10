import pytest
import pandas as pd
import sqlite3

from dashboard_public_health.application.query_service import (
    build_where_clause,
    filter_records_with_connection,
)
from dashboard_public_health.infrastructure.db import get_conn


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
