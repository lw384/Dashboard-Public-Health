# src/dashboard_public_health/application/auto_mapper.py


def auto_match_columns(df):
    """
    Automatically map CSV columns to internal schema names.

    Strategy:
      - Normalise column names first (lowercase + underscores)
      - Match exact names if present
      - Otherwise, match using keyword heuristics
      - Return dict: { internal_schema_field : csv_column_name }
    """

    cols = list(df.columns)
    colmap = {}

    def find(*keywords):
        """
        Find first column that contains ALL keyword fragments.
        Example: find("prevalence", "rate") will match prevalence_ratepercent.
        """
        for c in cols:
            if all(k in c for k in keywords):
                return c
        return None

    # Mapping rules
    rules = {
        "country": [("country",), ("nation",), ("location",)],
        "year": [("year",), ("yr",)],
        "disease": [("disease", "name"), ("disease",)],
        "disease_category": [("category",), ("class",)],
        "prevalence_ratepercent": [("prevalence",), ("prev_rate",)],
        "incidence_ratepercent": [("incidence",), ("new", "cases")],
        "mortality_ratepercent": [("mortality",), ("death",)],
        "population_affected": [("population", "affected"), ("affected",)],
        "recovery_ratepercent": [("recovery",), ("recover",)],
        "dalys": [("dalys",), ("burden",)],
        "healthcare_accesspercent": [("healthcare", "access"), ("med", "access")],
        "doctors_per_1000": [("doctor",), ("physician",)],
        "hospital_beds_per_1000": [("hospital_beds",), ("beds",)],
        "per_capita_income_usd": [("income",), ("gdp",)],
        "education_index": [("education",), ("edu",)],
        "urbanization_ratepercent": [("urban",), ("urbanization",)],
        "age_group": [("age_group",), ("age", "group")],
        "gender": [("gender",), ("sex",)],
        "availability_of_vaccines_treatment": [
            ("vaccine",),
            ("treatment",),
            ("availability",),
        ],
    }

    # Apply rules
    for internal_key, patterns in rules.items():
        for pattern in patterns:
            match = find(*pattern)
            if match:
                colmap[internal_key] = match
                break

    return colmap
