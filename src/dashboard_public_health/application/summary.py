# src/dashboard_public_health/application/summary_service.py

import pandas as pd
from time import perf_counter
from dashboard_public_health.infrastructure.logger import logger


# -------------------------------------------------------------
# 1. Descriptive summary
# -------------------------------------------------------------
def descriptive_summary(df: pd.DataFrame) -> str:
    numeric = df.select_dtypes(include="number")
    start = perf_counter()

    out = []
    out.append("📊 Basic Statistics\n")
    desc = numeric.describe().T

    for col, row in desc.iterrows():
        out.append(
            f"- {col}: mean={row['mean']:.2f}, min={row['min']:.2f}, max={row['max']:.2f}"
        )
    duration = perf_counter() - start
    logger.info(f"[perf] descriptive_summary duration={duration:.4f}s")
    return "\n".join(out)


# -------------------------------------------------------------
# 2. Time trends
# -------------------------------------------------------------
def time_trend_summary(df: pd.DataFrame) -> str:
    start = perf_counter()
    if "year" not in df:
        return "⚠ No 'year' column available."

    trend = df.groupby("year")[
        ["prevalence_rate", "incidence_rate", "mortality_rate"]
    ].mean()

    out = ["📈 Trends Over Time\n", "Year   Prev   Inc   Mort"]

    for year, row in trend.iterrows():
        out.append(
            f"{year:<6} {row['prevalence_rate']:.2f}  {row['incidence_rate']:.2f}  {row['mortality_rate']:.2f}"
        )

    duration = perf_counter() - start
    logger.info(f"[perf] time_trend_summary duration={duration:.4f}s")

    return "\n".join(out)


# -------------------------------------------------------------
# 3. Grouped stats
# -------------------------------------------------------------
def grouped_summary(df: pd.DataFrame, col: str) -> str:
    start = perf_counter()
    if col not in df.columns:
        return f"⚠ Column '{col}' does not exist."

    grouped = df.groupby(col)[
        ["prevalence_rate", "incidence_rate", "mortality_rate"]
    ].mean()

    out = [f"📚 Grouped by {col}\n", f"{col:<15} Prev   Inc    Mort"]

    for name, row in grouped.iterrows():
        out.append(
            f"{str(name):<15} {row['prevalence_rate']:.2f}  {row['incidence_rate']:.2f}  {row['mortality_rate']:.2f}"
        )

    duration = perf_counter() - start
    logger.info(f"[perf] grouped_summary duration={duration:.4f}s col={col}")

    return "\n".join(out)


# -------------------------------------------------------------
# 4. Correlation summary
# -------------------------------------------------------------
def correlation_summary(df: pd.DataFrame) -> str:
    numeric = df.select_dtypes(include="number")
    corr = numeric.corr()

    out = ["🔗 Correlation Matrix (selected pairs):"]

    # Show only key correlations
    pairs = [
        ("prevalence_rate", "mortality_rate"),
        ("prevalence_rate", "urbanization_rate"),
        ("mortality_rate", "per_capita_income"),
        ("prevalence_rate", "education_index"),
    ]

    for a, b in pairs:
        if a in corr and b in corr:
            out.append(f"- {a} ↔ {b}: {corr[a][b]:.3f}")

    return "\n".join(out)
