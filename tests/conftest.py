# tests/conftest.py
from pathlib import Path
import pytest

from dashboard_public_health import config


@pytest.fixture
def sample_csv_path(project_root=config.PROJECT_ROOT) -> Path:
    return project_root / "tests" / "data" / "sample_data.csv"


@pytest.fixture
def temp_db_path(tmp_path, monkeypatch):
    """
    Use pytest tmp_path and monkeypatch config.DB_PATH to avoid touching real data/public_health.db
    """
    db_path = tmp_path / "test_public_health.db"
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return db_path
