import pandas as pd
from dashboard_public_health.ui.cli.session import SessionContext
from dashboard_public_health.domain.models import FilterCriteria


def test_session_context_stores_filters_and_df():
    ctx = SessionContext()
    filters = FilterCriteria(country="UK", year_from=2000)
    df = pd.DataFrame({"country": ["UK"], "year": [2000]})

    ctx.filters = filters
    ctx.last_df = df
    ctx.last_export_path = "outputs/test.csv"

    assert ctx.filters.country == "UK"
    assert ctx.last_df.equals(df)
    assert ctx.last_export_path == "outputs/test.csv"
