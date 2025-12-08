import pandas as pd
from dashboard_public_health.application.visualization_service import plot_trend


def test_plot_trend_creates_file(tmp_path):
    # Prepare test DataFrame
    df = pd.DataFrame({"date": ["2020-01-01", "2020-01-02"], "value": [10, 20]})

    # Path inside pytest temp folder
    out_file = tmp_path / "trend_test.png"

    # Call visualization function
    result_path = plot_trend(df, output_path=str(out_file))

    # Assertions
    assert out_file.exists(), "Trend PNG file was not created."
    assert result_path == str(out_file), "Returned file path is incorrect."
    assert out_file.stat().st_size > 0, "Output PNG is empty."


def test_plot_trend_handles_empty_df(tmp_path):
    df = pd.DataFrame(columns=["date", "value"])

    out_file = tmp_path / "empty_trend.png"

    result = plot_trend(df, output_path=str(out_file))

    # Should return None and not crash
    assert result is None
    assert not out_file.exists(), "Plot should not be created for empty df."


from dashboard_public_health.application.visualization_service import plot_grouped_bar


def test_plot_grouped_bar_creates_file(tmp_path):
    df = pd.DataFrame({"country": ["UK", "UK", "US"], "value": [10, 20, 5]})

    out_file = tmp_path / "grouped_bar.png"

    result_path = plot_grouped_bar(df, group_col="country", output_path=str(out_file))

    assert out_file.exists()
    assert result_path == str(out_file)
    assert out_file.stat().st_size > 0


def test_plot_grouped_bar_invalid_group_col(tmp_path):
    df = pd.DataFrame({"value": [10, 20]})
    out_file = tmp_path / "bad_group.png"

    result = plot_grouped_bar(df, group_col="missing_col", output_path=str(out_file))

    assert result is None
    assert not out_file.exists()
