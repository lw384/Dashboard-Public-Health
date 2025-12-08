# src/dashboard_public_health/application/visualization_service.py

import matplotlib.pyplot as plt
import pandas as pd

from dashboard_public_health.infrastructure.logger import log_action


@log_action
def plot_trend(df: pd.DataFrame, output_path="trend.png"):
    """
    Plot a time-series trend line chart from the filtered DataFrame.

    The DataFrame must contain 'date' and 'value' columns.
    """
    if df.empty:
        print("[visualization] No data to plot.")
        return None

    # Group by date (in case multiple rows per date)
    trend = df.groupby("date")["value"].mean()

    plt.figure(figsize=(10, 5))
    trend.plot(kind="line")

    plt.title("Trend over time")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)

    print(f"[visualization] Trend chart saved to {output_path}")
    return output_path


@log_action
def plot_grouped_bar(
    df: pd.DataFrame, group_col="country", output_path="grouped_bar.png"
):
    """
    Plot a bar chart showing average value grouped by country or age_group.
    """

    if group_col not in df.columns:
        print(f"[visualization] Column '{group_col}' not found.")
        return None

    grouped = df.groupby(group_col)["value"].mean().sort_values()

    plt.figure(figsize=(10, 5))
    grouped.plot(kind="bar")

    plt.title(f"Average Value by {group_col.capitalize()}")
    plt.xlabel(group_col.capitalize())
    plt.ylabel("Average Value")
    plt.tight_layout()
    plt.savefig(output_path)

    print(f"[visualization] Grouped bar chart saved to {output_path}")
    return output_path
