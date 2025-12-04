"""Module providing a function to read CSV file."""

from pathlib import Path
import pandas as pd


def load_csv_to_df(csv_path: str) -> pd.DataFrame:
    """Read a CSV file into a pandas DataFrame."""
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    df = pd.read_csv(path)
    return df
