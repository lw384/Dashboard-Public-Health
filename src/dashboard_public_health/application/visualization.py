import pandas as pd
import matplotlib.pyplot as plt


def plot_descriptive(df):
    numeric = df.select_dtypes(include="number")
    desc = numeric.describe().T  # rows = features

    plt.figure(figsize=(10, 4))
    desc["mean"].plot(kind="bar")
    plt.title("Mean Values of Numeric Features")
    plt.ylabel("Mean")
    plt.tight_layout()
    plt.show()


def plot_time_trends(df):
    trend = df.groupby("year")[
        ["prevalence_rate", "incidence_rate", "mortality_rate"]
    ].mean()
    plt.figure(figsize=(10, 4))
    for col in trend.columns:
        plt.plot(trend.index, trend[col], label=col)
    plt.legend()
    plt.xlabel("Year")
    plt.ylabel("Rate")
    plt.title("Trends Over Time")
    plt.tight_layout()
    plt.show()


def plot_grouped(df, col):
    grouped = df.groupby(col)[
        ["prevalence_rate", "incidence_rate", "mortality_rate"]
    ].mean()
    grouped.plot(kind="bar", figsize=(12, 5))
    plt.title(f"Grouped Stats by {col}")
    plt.tight_layout()
    plt.show()


def plot_corr(df):
    numeric = df.select_dtypes(include="number")
    # drop identifiers/time columns from correlation heatmap
    for col in ["id", "year"]:
        if col in numeric.columns:
            numeric = numeric.drop(columns=[col])
    corr = numeric.corr()
    plt.figure(figsize=(10, 8))
    plt.imshow(corr, cmap="coolwarm")
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.show()
