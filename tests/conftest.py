# tests/conftest.py
from pathlib import Path
import pytest

from dashboard_public_health import config


@pytest.fixture
def sample_csv_path(project_root: Path) -> Path:
    return project_root / "tests" / "data" / "sample_public_health.csv"


@pytest.fixture
def temp_db_path(tmp_path, monkeypatch):
    """
    使用 pytest 自带的 tmp_path 临时目录，
    并 monkeypatch 掉 config.DB_PATH,避免测试污染真实 data/public_health.db
    """
    db_path = tmp_path / "test_public_health.db"
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return db_path
