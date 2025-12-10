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

    # 根据你的数据编码调整 encoding / sep
    df = pd.read_csv(path)

    # 可选：简单打印一下，方便调试
    print(f"[file_loader] Loaded {len(df)} rows from {path}")
    return df
