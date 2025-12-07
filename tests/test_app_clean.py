# tests/application/test_clean.py
import pandas as pd
import pytest

from dashboard_public_health.application.clean import (
    map_raw_to_internal_schema,
    clean_internal_dataframe,
    transform_raw_health_csv,
)


@pytest.fixture
def raw_health_df() -> pd.DataFrame:
    """
    构造一个模拟的原始 epidemiological CSV DataFrame，
    列名故意用不同大小写和空格，方便测试 _normalise_columns 和映射逻辑。
    """
    data = {
        "Age": [10, 30, None],  # 第3行 age 缺失
        "Location": [" Urban ", "Rural", "Urban"],
        "Daily_New_Cases": [5, "not-a-number", 8],  # 第2行是非法数值
        "Date_of_Data_Collection": [
            "2024-01-01",
            "bad-date",  # 第2行是非法日期
            "2024-03-15",
        ],
    }
    return pd.DataFrame(data)


def test_map_raw_to_internal_schema_happy_path(raw_health_df: pd.DataFrame):
    """
    map_raw_to_internal_schema 应该：
      - 规范列名后成功找到 age/location/daily_new_cases/date_of_data_collection
      - 输出包含预期的内部列：age, country, value, date, indicator, age_group, source_file
      - indicator 固定为 'daily_new_cases'
      - country 使用 Location 的值
      - age_group 按年龄分段
      - source_file 使用传入的 source_name
    """
    df_internal = map_raw_to_internal_schema(raw_health_df, source_name="test_source")

    # 列是否齐全
    expected_cols = {
        "age",
        "country",
        "value",
        "date",
        "indicator",
        "age_group",
        "source_file",
    }
    assert expected_cols.issubset(set(df_internal.columns))

    # indicator 应该全部是 'daily_new_cases'
    assert set(df_internal["indicator"]) == {"daily_new_cases"}

    # country 源于 Location（注意去掉空格的 Urban）
    assert (
        "Urban" in df_internal["country"].values
        or " Urban " in df_internal["country"].values
    )
    assert "Rural" in df_internal["country"].values

    # 年龄段分组：10 -> 0-17，30 -> 18-49，None -> Unknown（映射阶段先给 Unknown）
    # 不保证顺序，所以用集合比较
    assert "0-17" in set(df_internal["age_group"])
    assert "18-49" in set(df_internal["age_group"])
    assert "Unknown" in set(df_internal["age_group"])

    # source_name 要被传递到 source_file
    assert set(df_internal["source_file"]) == {"test_source"}


def test_map_raw_to_internal_schema_missing_required_columns_raises():
    """
    如果缺少必需列（如 daily_new_cases），应该抛 ValueError。
    """
    df_bad = pd.DataFrame(
        {
            "Age": [20, 30],
            "Location": ["Urban", "Rural"],
            # 缺少 Daily_New_Cases
            "Date_of_Data_Collection": ["2024-01-01", "2024-01-02"],
        }
    )

    with pytest.raises(ValueError) as excinfo:
        map_raw_to_internal_schema(df_bad)

    assert "missing required columns" in str(excinfo.value)


def test_clean_internal_dataframe_drops_invalid_date_and_value(
    raw_health_df: pd.DataFrame,
):
    """
    clean_internal_dataframe 应该：
      - 丢弃非法日期行（bad-date）
      - 丢弃非法数值行（not-a-number）
      - 将 date 统一为 'YYYY-MM-DD' 字符串
      - 将 value 转换为 float
      - 删除 age 列（如果存在）
    """
    df_internal = map_raw_to_internal_schema(raw_health_df, source_name="test_source")
    df_clean = clean_internal_dataframe(df_internal)

    # 预期：第 0 行和第 2 行是有效的；第 1 行因日期+数值非法被丢弃
    assert len(df_clean) == 2

    # 所有日期字符串应该是 YYYY-MM-DD 格式
    for d in df_clean["date"]:
        assert isinstance(d, str)
        assert len(d) == 10
        assert d.count("-") == 2

    # value 应该是 float 类型
    assert df_clean["value"].dtype == "float64"

    # age 列应该被删除（我们内部 schema 不再需要它）
    assert "age" not in df_clean.columns

    # 字符串字段应该被 strip
    assert all(
        not c.startswith(" ") and not c.endswith(" ") for c in df_clean["country"]
    )


def test_transform_raw_health_csv_full_pipeline(raw_health_df: pd.DataFrame):
    """
    transform_raw_health_csv：从原始 df 一步到清洗后的内部 df。
    应该产出：
      - 列：date, country, indicator, value, age_group, source_file
      - 行数：2（去掉非法行）
    """
    df_clean = transform_raw_health_csv(raw_health_df, source_name="pipeline_test")

    expected_cols = {
        "date",
        "country",
        "indicator",
        "value",
        "age_group",
        "source_file",
    }
    assert expected_cols == set(df_clean.columns)

    # 行数符合预期（第 1 行非法被丢弃）
    assert len(df_clean) == 2

    # indicator 全部正确
    assert set(df_clean["indicator"]) == {"daily_new_cases"}

    # source_file 正确传递
    assert set(df_clean["source_file"]) == {"pipeline_test"}

    # 年龄分组合理：0-17 和 18-49 各出现一次
    age_groups = set(df_clean["age_group"])
    assert "0-17" in age_groups
    assert "Unknown" in age_groups
