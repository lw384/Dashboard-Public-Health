# src/dashboard_public_health/ui/cli/helpers.py
import builtins
from dashboard_public_health.domain.models import FilterCriteria


def ask_filter_inputs():
    """Legacy wrapper kept for backward compatibility; delegates to collect_filters."""
    return collect_filters()


def collect_filters(input_func=None, defaults=None) -> FilterCriteria:
    """
    Unified filter collector used by menus and tests.

    - input_func: dependency-injected input reader for testability.
    - defaults: previous filter state; blank input keeps prior values.
    """

    input_func = input_func or builtins.input
    # allow defaults to be a dict or FilterCriteria; normalize to dict
    if isinstance(defaults, FilterCriteria):
        defaults = defaults.__dict__
    defaults = defaults or {}

    def read_str(key, prompt):
        val = input_func(prompt).strip()
        return val or defaults.get(key)

    def read_int(key, prompt):
        val = input_func(prompt).strip()
        if val == "":
            return defaults.get(key)
        try:
            return int(val)
        except ValueError:
            return defaults.get(key)

    def read_float(key, prompt):
        val = input_func(prompt).strip()
        if val == "":
            return defaults.get(key)
        try:
            return float(val)
        except ValueError:
            return defaults.get(key)

    try:
        filters = {
            "country": read_str("country", "Country (blank = none): "),
            "disease": read_str("disease", "Disease (blank = none): "),
            "disease_category": read_str("disease_category", "Disease category (blank = none): "),
            "age_group": read_str("age_group", "Age group (blank = none): "),
            "gender": read_str("gender", "Gender (blank = none): "),
            "year_from": read_int("year_from", "Year from (blank = none): "),
            "year_to": read_int("year_to", "Year to (blank = none): "),
            "min_urbanization_rate": read_float(
                "min_urbanization_rate", "Min urbanization rate (%): "
            ),
            "min_healthcare_access": read_float(
                "min_healthcare_access", "Min healthcare access (%): "
            ),
            "min_hospital_beds": read_float(
                "min_hospital_beds", "Min hospital beds per 1000: "
            ),
            "min_income": read_float("min_income", "Min per capita income: "),
            "min_education": read_float("min_education", "Min education index: "),
        }
    except KeyboardInterrupt:
        print("\n[filter] Cancelled.")
        return None

    return FilterCriteria(**filters)
