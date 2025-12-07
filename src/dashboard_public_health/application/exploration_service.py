from dashboard_public_health.infrastructure.db import fetch_all_records
from dashboard_public_health.domain.models import FilterCriteria
from dashboard_public_health.domain.rules import (
    apply_filter,
)
from dashboard_public_health.domain.analysis import (
    calculate_summary,
    group_by_country,
)


def filter_and_summarise(
    country: str | None, start_year: int | None, end_year: int | None
):
    records = fetch_all_records()
    criteria = FilterCriteria(country=country, start_year=start_year, end_year=end_year)
    filtered = apply_filter(records, criteria)
    summary = calculate_summary(filtered)
    grouped = group_by_country(filtered)
    return summary, grouped
