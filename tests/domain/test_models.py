import pytest
from dashboard_public_health.domain.models import HealthRecord


def _sample_record_dict():
    return {
        "country": "France",
        "year": 2021,
        "disease": "COVID-19",
        "disease_category": "Viral",
        "prevalence_rate": 10.5,
        "incidence_rate": 9.1,
        "mortality_rate": 2.3,
        "population_affected": 123456,
        "recovery_rate": 85.0,
        "dalys": 1200.0,
        "healthcare_access": 75.0,
        "doctors_per_1000": 3.5,
        "hospital_beds_per_1000": 4.2,
        "per_capita_income": 42000.0,
        "education_index": 0.81,
        "urbanization_rate": 78.0,
        "age_group": "50-64",
        "gender": "Female",
        "treatment_available": "Yes",
        "source_file": "test.csv",
    }


def test_healthrecord_from_dict_and_to_tuple():
    data = _sample_record_dict()
    record = HealthRecord.from_dict(data)

    assert record.country == "France"
    assert record.disease_category == "Viral"

    # to_db_tuple should align with insert order in db.py
    expected_prefix = (
        data["country"],
        data["year"],
        data["disease"],
        data["disease_category"],
        data["prevalence_rate"],
        data["incidence_rate"],
        data["mortality_rate"],
        data["population_affected"],
        data["recovery_rate"],
        data["dalys"],
        data["healthcare_access"],
        data["doctors_per_1000"],
        data["hospital_beds_per_1000"],
        data["per_capita_income"],
        data["education_index"],
        data["urbanization_rate"],
        data["age_group"],
        data["gender"],
        data["treatment_available"],
        data["source_file"],
    )

    assert record.to_db_tuple() == expected_prefix
