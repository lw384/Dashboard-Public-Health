# tests/data_access/test_loader.py
from dashboard_public_health.infrastructure.csv_reader import load_csv


def test_load_csv_raises_if_file_not_found(tmp_path):
    fake_path = tmp_path / "non_existent.csv"
    # TDD: expected behavior first
    try:
        load_csv(fake_path)
        assert False, "Expected FileNotFoundError but none was raised"
    except FileNotFoundError:
        assert True


def test_load_csv_reads_rows(sample_csv_path):
    df = load_csv(sample_csv_path)

    # Should read at least a few rows
    assert len(df) >= 1
    # Column names should include expected raw fields
    assert "Date" in df.columns
    assert "Country" in df.columns
