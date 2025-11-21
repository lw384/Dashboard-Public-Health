import pandas as pd
import pytest
from pathlib import Path

from dashboard_public_health.data_access.loader import load_csv_to_df


def test_load_csv_success(tmp_path):
    """Test loading a correct CSV file returns a DataFrame."""
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text("country,cases\na,1\nb,2\n")

    df = load_csv_to_df(str(csv_file))

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert df["country"].tolist() == ["a", "b"]
    assert df["cases"].tolist() == [1, 2]


def test_load_csv_with_path_object(tmp_path):
    """Test load_csv_to_df also accepts a Path object."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("col\n123\n")

    df = load_csv_to_df(csv_file)

    assert isinstance(df, pd.DataFrame)
    assert df["col"].tolist() == [123]


def test_missing_file_raises():
    """Non-existent file should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_csv_to_df("this_file_does_not_exist.csv")


def test_empty_csv_file(tmp_path):
    """
    If CSV file is empty, pandas raises EmptyDataError.
    Test that the error is correctly propagated.
    """
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")  # completely empty file

    with pytest.raises(pd.errors.EmptyDataError):
        load_csv_to_df(empty_file)


# def test_invalid_csv_format(tmp_path):
#     """CSV with invalid format should raise pandas ParserError."""
#     bad_file = tmp_path / "bad.csv"
#     bad_file.write_text("a,b\n1,2,3\n")
#     bad_file.write_text("invalid line without commas")

#     with pytest.raises(pd.errors.ParserError):
#         load_csv_to_df(bad_file)
