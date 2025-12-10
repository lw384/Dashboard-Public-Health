import pandas as pd
from dashboard_public_health.application.auto_mapper import auto_match_columns


def test_auto_match_columns_new_dataset():
    df = pd.DataFrame(
        columns=[
            "Country",
            "Year",
            "Disease Name",
            "Disease Category",
            "Prevalence Rate (%)",
            "Incidence Rate (%)",
            "Mortality Rate (%)",
            "Population Affected",
            "Healthcare Access (%)",
            "Age Group",
            "Gender",
            "Availability of Vaccines/Treatment",
        ]
    )

    mapping = auto_match_columns(df)

    # core required fields
    assert mapping["country"] == "country"
    assert mapping["year"] == "year"
    assert mapping["disease"] == "disease_name"
    assert mapping["disease_category"] == "disease_category"
    assert mapping["prevalence_rate"] == "prevalence_rate_%"
    assert mapping["incidence_rate"] == "incidence_rate_%"
    assert mapping["mortality_rate"] == "mortality_rate_%"
    assert mapping["population_affected"] == "population_affected"
    assert mapping["healthcare_access"] == "healthcare_access_%"

    # optional fields
    assert mapping["age_group"] == "age_group"
    assert mapping["gender"] == "gender"
    assert mapping["treatment_available"] == "availability_of_vaccines/treatment"
