import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from dashboard_public_health.application.visualization import (
    plot_descriptive,
    plot_time_trends,
    plot_grouped,
    plot_corr,
)

matplotlib.use("Agg")  # prevent GUI windows during tests


# --------------------------
# Helper: Create sample Data
# --------------------------
def sample_df():
    return pd.DataFrame(
        {
            "year": [2000, 2001, 2002, 2003],
            "prevalence_rate": [10, 12, 11, 13],
            "incidence_rate": [5, 6, 5.5, 7],
            "mortality_rate": [2, 2.5, 2.2, 3],
            "population_affected": [100, 150, 120, 200],
            "disease": ["A", "A", "B", "B"],
        }
    )


# --------------------------
# Test: plot_descriptive
# --------------------------
def test_plot_descriptive():
    df = sample_df()
    plot_descriptive(df)

    fig = plt.gcf()
    assert len(fig.axes) > 0  # a plot was created


# --------------------------
# Test: plot_time_trends
# --------------------------
def test_plot_time_trends():
    df = sample_df()
    plot_time_trends(df)

    fig = plt.gcf()
    assert len(fig.axes) > 0  # line chart was created

    # Each epidemiological metric produces a line
    ax = fig.axes[0]
    assert len(ax.lines) == 3  # prevalence + incidence + mortality


# --------------------------
# Test: plot_grouped
# --------------------------
def test_plot_grouped():
    df = sample_df()
    plot_grouped(df, "disease")

    fig = plt.gcf()
    assert len(fig.axes) > 0

    ax = fig.axes[0]
    # grouped bar chart: each disease = 2 groups → 2 bars per metric
    assert len(ax.patches) > 0  # bars exist


# --------------------------
# Test: plot_corr
# --------------------------
def test_plot_corr():
    df = sample_df()
    plot_corr(df)

    fig = plt.gcf()
    assert len(fig.axes) > 0  # heatmap exists

    ax = fig.axes[0]
    # heatmap should have image data
    assert len(ax.images) == 1
