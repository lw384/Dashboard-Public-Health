# src/dashboard_public_health/application/clean.py
from __future__ import annotations
import math
from dataclasses import dataclass
from datetime import date
from typing import Optional

import pandas as pd


# ---------- 内部领域模型（可选，用来解释你的 schema） ----------
@dataclass
class PublicHealthRecord:
    date: date
    country: str
    indicator: str
    value: float
    age_group: Optional[str] = None
    source_file: Optional[str] = None


# ---------- 工具函数：列名归一化 ----------
def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lower-case all column names and replace spaces with underscores.
    This makes matching more robust across different CSV variants.
    """
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


# ---------- 工具函数：年龄 → 年龄段 ----------
def _map_age_to_group(age: float | int | None) -> str:
    try:
        a = float(age)
    except (TypeError, ValueError):
        return "Unknown"

    if math.isnan(a):
        return "Unknown"

    if a < 18:
        return "0-17"
    if a < 50:
        return "18-49"
    if a < 65:
        return "50-64"
    return "65+"


# ---------- 映射 + 选择我们关心的列 ----------
def map_raw_to_internal_schema(
    df_raw: pd.DataFrame, *, source_name: str = "health_csv"
) -> pd.DataFrame:
    """
    Transform the raw epidemiological CSV into the internal schema:
    [date, country, indicator, value, age_group, source_file]

    Expected raw columns (case-insensitive, underscores allowed):
        - age
        - location
        - daily_new_cases
        - date_of_data_collection

    Raises:
        ValueError if required columns are missing.
    """
    df = _normalise_columns(df_raw)

    required_cols = {"age", "location", "daily_new_cases", "date_of_data_collection"}
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")

    # 只提取我们关心的列
    df_internal = pd.DataFrame()
    df_internal["age"] = df["age"]
    df_internal["country"] = df["location"]  # 用 Location 当作地区
    df_internal["value"] = df["daily_new_cases"]
    df_internal["date"] = df["date_of_data_collection"]

    # 固定指标类型
    df_internal["indicator"] = "daily_new_cases"

    # 派生年龄段
    df_internal["age_group"] = df_internal["age"].apply(_map_age_to_group)

    # 来源信息（可选）
    df_internal["source_file"] = source_name

    return df_internal


# ---------- 类型转换 + 缺失值处理 ----------
def clean_internal_dataframe(df_internal: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the internal schema dataframe:
      - drop rows with missing critical fields
      - parse date to ISO string
      - convert value to float
      - strip strings
    """
    df = df_internal.copy()

    # 丢掉关键字段缺失的数据
    df = df.dropna(subset=["date", "country", "indicator", "value"])

    # 日期 → datetime → ISO 字符串
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # 数值 → float
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    df["value"] = df["value"].astype(float)

    # 字符串清洗
    df["country"] = df["country"].astype(str).str.strip()
    df["indicator"] = df["indicator"].astype(str).str.strip()
    df["age_group"] = df["age_group"].astype(str).str.strip()
    df["source_file"] = df["source_file"].astype(str).str.strip()

    # 不再需要原始 age 列（如果你不想存它）
    if "age" in df.columns:
        df = df.drop(columns=["age"])

    return df


# ---------- 对外暴露的清洗入口 ----------
def transform_raw_health_csv(
    df_raw: pd.DataFrame, *, source_name: str = "health_csv"
) -> pd.DataFrame:
    """
    High-level transformation:
        raw CSV -> internal schema -> cleaned internal dataframe.
    """
    df_internal = map_raw_to_internal_schema(df_raw, source_name=source_name)
    df_clean = clean_internal_dataframe(df_internal)
    return df_clean
