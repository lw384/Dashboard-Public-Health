# infrastructure/csv_reader.py
from pathlib import Path
import pandas as pd


def load_csv(csv_path: str) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.

    :param csv_path: Path to the CSV file.
    :return: DataFrame with raw data.
    """
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    # Adjust encoding/sep if your dataset differs
    df = pd.read_csv(path)

    # Optional: print basic info for debugging
    print(f"[file_loader] Loaded {len(df)} rows from {path}")
    return df
