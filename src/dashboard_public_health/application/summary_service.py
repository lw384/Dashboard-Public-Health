# src/dashboard_public_health/application/summary_service.py
"""
Summary service providing high-level analytical insights for 4 major use cases:
1. Healthcare Policy Analysis
2. Epidemiological Studies
3. Machine Learning Preparation
4. Global Health Research
"""

import pandas as pd


# ---------------------------------------------
# Helper: safe return for empty DataFrames
# ---------------------------------------------
def _empty_summary(name: str):
    return {"error": f"No data available for {name}. Please adjust filters."}


# ---------------------------------------------
# Use Case 1: Healthcare Policy Summary
# ---------------------------------------------
def compute_policy_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return _empty_summary("Healthcare Policy Summary")

    summary = {}

    summary["avg_prevalence"] = df["prevalence_rate"].mean()
    summary["avg_incidence"] = df["incidence_rate"].mean()
    summary["avg_mortality"] = df["mortality_rate"].mean()

    # Country-level severity ranking
    country_mean = (
        df.groupby("country")["prevalence_rate"].mean().sort_values(ascending=False)
    )
    summary["highest_prevalence_country"] = country_mean.head(5).to_dict()

    # Medical resource summary
    summary["resources"] = {
        "mean_doctors_per_1000": df["doctors_per_1000"].mean(),
        "mean_hospital_beds_per_1000": df["hospital_beds_per_1000"].mean(),
        "mean_healthcare_access": df["healthcare_access"].mean(),
    }

    # Economic correlations
    if df["per_capita_income"].notna().sum() > 5:
        summary["economic_correlations"] = {
            "income_vs_mortality": df["per_capita_income"].corr(df["mortality_rate"]),
            "education_vs_prevalence": df["education_index"].corr(
                df["prevalence_rate"]
            ),
        }
    else:
        summary["economic_correlations"] = "Not enough data"

    return summary


# ---------------------------------------------
# Use Case 2: Epidemiological Summary
# ---------------------------------------------
def compute_epidemiology_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return _empty_summary("Epidemiological Summary")

    summary = {}

    # Trend over time
    trend = df.groupby("year")[
        ["prevalence_rate", "incidence_rate", "mortality_rate"]
    ].mean()
    summary["yearly_trend"] = trend.to_dict()

    # Disease category comparison
    summary["disease_category_stats"] = (
        df.groupby("disease_category")["prevalence_rate"]
        .mean()
        .sort_values(ascending=False)
        .to_dict()
    )

    # Correlations with socio-economic/environmental indicators
    cols = [
        "prevalence_rate",
        "mortality_rate",
        "incidence_rate",
        "urbanization_rate",
        "education_index",
        "per_capita_income",
    ]
    corr = df[cols].corr()
    summary["correlations"] = corr.to_dict()

    return summary


# ---------------------------------------------
# Use Case 3: Machine Learning Preparation
# ---------------------------------------------
def compute_ml_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return _empty_summary("Machine Learning Prep Summary")

    summary = {}

    numeric_cols = df.select_dtypes(include="number").columns

    # Missing values
    summary["missing_values"] = df.isna().sum().to_dict()

    # Feature distribution
    summary["feature_stats"] = df[numeric_cols].describe().to_dict()

    # Label balance
    summary["disease_distribution"] = df["disease"].value_counts().head(20).to_dict()

    # Outliers (99th percentile)
    summary["outlier_thresholds"] = df[numeric_cols].quantile(0.99).to_dict()

    return summary


# ---------------------------------------------
# Use Case 4: Global Health Summary
# ---------------------------------------------
def compute_global_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return _empty_summary("Global Health Summary")

    summary = {}

    # Top-N high mortality
    summary["top_mortality_countries"] = (
        df.groupby("country")["mortality_rate"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .to_dict()
    )

    # Global trends
    summary["global_trend"] = df.groupby("year")["prevalence_rate"].mean().to_dict()

    # Disease burden (DALYs)
    summary["disease_burden"] = (
        df.groupby("disease")["dalys"]
        .sum()
        .sort_values(ascending=False)
        .head(20)
        .to_dict()
    )

    return summary


def format_policy_report(summary: dict) -> str:
    """Convert raw summary metrics into a readable human-friendly report."""

    lines = []
    lines.append("=== Public Health Summary Report ===")

    # --- Epidemiological Overview ---
    lines.append("\n🦠 Epidemiological Overview")
    lines.append(f"- Average prevalence rate: {summary['avg_prevalence']:.2f}%")
    lines.append(f"- Average incidence rate: {summary['avg_incidence']:.2f}%")
    lines.append(f"- Average mortality rate: {summary['avg_mortality']:.2f}%")

    # --- Highest Burden ---
    highest = summary["highest_prevalence_country"]
    for country, value in highest.items():
        lines.append(
            f"\n🌍 Country with highest disease burden: {country} ({value:.2f}% prevalence)"
        )

    # --- Healthcare Resources ---
    res = summary["resources"]
    lines.append("\n🏥 Healthcare System Capacity")
    lines.append(
        f"- Doctors per 1000 people: {float(res['mean_doctors_per_1000']):.2f}"
    )
    lines.append(
        f"- Hospital beds per 1000: {float(res['mean_hospital_beds_per_1000']):.2f}"
    )
    lines.append(f"- Healthcare access: {float(res['mean_healthcare_access']):.2f}%")

    # --- Correlations ---
    corr = summary["economic_correlations"]
    lines.append("\n📈 Socio-economic Correlations")
    lines.append(
        f"- Income vs Mortality: {float(corr['income_vs_mortality']):.3f} "
        "(negative = higher income lowers mortality)"
    )
    lines.append(
        f"- Education vs Prevalence: {float(corr['education_vs_prevalence']):.3f} "
        "(negative = more education lowers prevalence)"
    )

    return "\n".join(lines)


def format_epidemiology_report(summary: dict) -> str:
    """Human-readable Epidemiological Summary"""

    if "error" in summary:
        return summary["error"]

    lines = []
    lines.append("=== Epidemiological Summary ===\n")

    # ---------------- Yearly Trends ----------------
    lines.append("📊 Yearly Disease Trends (Average %)")

    trend = summary["yearly_trend"]  # dict like {"prevalence_rate": {...}, ...}
    years = list(trend["prevalence_rate"].keys())

    lines.append("Year   Prev   Inc    Mort")

    for year in years:
        prev = trend["prevalence_rate"][year]
        inc = trend["incidence_rate"][year]
        mort = trend["mortality_rate"][year]
        lines.append(f"{year}   {prev:5.2f}  {inc:5.2f}  {mort:5.2f}")

    # ---------------- Category Comparison ----------------
    lines.append("\n🦠 Disease Category Impact (Avg Prevalence)")
    cat_stats = summary["disease_category_stats"]

    for i, (cat, val) in enumerate(cat_stats.items(), start=1):
        lines.append(f"{i}. {cat} — {val:.2f}%")

    # ---------------- Correlations ----------------
    lines.append("\n📈 Key Correlations (Socio-Economic / Environment)")

    corr = summary["correlations"]

    # choose only meaningful pairs
    pairs = [
        ("Education vs Prevalence", corr["education_index"]["prevalence_rate"]),
        ("Income vs Mortality", corr["per_capita_income"]["mortality_rate"]),
        ("Urbanization vs Incidence", corr["urbanization_rate"]["incidence_rate"]),
    ]

    for label, value in pairs:
        lines.append(f"- {label}: {value:.3f}")

    return "\n".join(lines)


def format_ml_report(summary: dict) -> str:
    """Pretty formatting for machine learning preparation summary."""
    if "error" in summary:
        return summary["error"]

    lines = []
    lines.append("=== Machine Learning Preparation Summary ===\n")

    # -------------------------------
    # Missing Values
    # -------------------------------
    lines.append("❗ Missing Values (per column):")
    for col, count in summary["missing_values"].items():
        lines.append(f"- {col}: {count}")
    lines.append("")

    # -------------------------------
    # Feature Statistics
    # -------------------------------
    lines.append("📊 Feature Summary Statistics:")
    feature_stats = summary["feature_stats"]

    # Only show key metrics rather than full dict
    key_metrics = ["mean", "std", "min", "25%", "50%", "75%", "max"]

    for col, stats in feature_stats.items():
        lines.append(f"- {col}:")
        for key in key_metrics:
            if key in stats:
                val = stats[key]
                # Convert numpy types safely
                try:
                    val = float(val)
                    lines.append(f"    {key:4}: {val:,.2f}")
                except Exception:
                    lines.append(f"    {key:4}: {val}")
        lines.append("")

    # -------------------------------
    # Disease Distribution
    # -------------------------------
    lines.append("🔢 Disease Distribution (Top 20 classes):")
    for disease, count in summary["disease_distribution"].items():
        lines.append(f"- {disease}: {count:,}")
    lines.append("")

    # -------------------------------
    # Outlier Thresholds
    # -------------------------------
    lines.append("⚠ Outlier Thresholds (99th percentile):")
    for col, val in summary["outlier_thresholds"].items():
        try:
            val = float(val)
            lines.append(f"- {col}: {val:,.2f}")
        except Exception:
            lines.append(f"- {col}: {val}")
    lines.append("")

    return "\n".join(lines)


def format_global_report(summary: dict) -> str:
    if "error" in summary:
        return summary["error"]

    lines = []
    lines.append("=== Global Health Summary ===")

    lines.append("\n💀 Top 10 Mortality Countries:")
    for c, v in summary["top_mortality_countries"].items():
        lines.append(f"- {c}: {v:.2f}")

    lines.append("\n🌍 Global Prevalence Trend:")
    for year, val in summary["global_trend"].items():
        lines.append(f"- {year}: {val:.2f}")

    lines.append("\n🏋 Disease Burden (DALYs):")
    for disease, val in summary["disease_burden"].items():
        lines.append(f"- {disease}: {val}")

    return "\n".join(lines)


def format_summary_report(summary: dict, mode: str) -> str:
    mode = mode.lower()

    if mode == "policy":
        return format_policy_report(summary)
    elif mode == "epidemiology":
        return format_epidemiology_report(summary)
    elif mode == "ml":
        return format_ml_report(summary)
    elif mode == "global":
        return format_global_report(summary)
    else:
        return "Unknown summary mode."


# ---------------------------------------------------
# Router: choose which summary to compute
# ---------------------------------------------------
def compute_summary(df: pd.DataFrame, mode: str) -> dict:
    mode = mode.lower()

    if mode == "policy":
        return compute_policy_summary(df)
    elif mode == "epidemiology":
        return compute_epidemiology_summary(df)
    elif mode == "ml":
        return compute_ml_summary(df)
    elif mode == "global":
        return compute_global_summary(df)
    else:
        return {"error": f"Unknown summary mode: {mode}"}
