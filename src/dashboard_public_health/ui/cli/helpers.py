# src/dashboard_public_health/ui/cli/helpers.py


def ask_filter_inputs():
    """Prompt user for filtering conditions."""
    country = input("Country (blank = none): ").strip() or None
    year = input("Year (blank = none): ").strip() or None
    disease = input("Disease (blank = none): ").strip() or None

    return {
        "country": country,
        "year": year,
        "disease": disease,
    }
