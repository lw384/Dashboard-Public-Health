# tests/data_access/test_loader.py
from dashboard_public_health.infrastructure.csv_reader import load_csv


def test_load_csv_raises_if_file_not_found(tmp_path):
    fake_path = tmp_path / "non_existent.csv"
    # TDD：先写这个期望行为
    try:
        load_csv(fake_path)
        assert False, "Expected FileNotFoundError but none was raised"
    except FileNotFoundError:
        assert True


def test_load_csv_reads_rows(sample_csv_path):
    df = load_csv(sample_csv_path)

    # 至少应该能读到几行
    assert len(df) >= 1
    # 列名应该包含我们期待的原始列
    assert "Date" in df.columns
    assert "Country" in df.columns
