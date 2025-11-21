import re
import importlib
import pytest
from dashboard_public_health.data_access import db


def test_db_url_format():
    """Check DB_URL format (no actual connection)."""

    url = db.DB_URL
    assert url.startswith("postgresql+psycopg://")
    # 简单验证格式是否包含 user:pass@host:port/db
    pattern = r"postgresql\+psycopg://.+:.+@.+:\d+/.+"
    assert re.match(pattern, url)


def test_engine_caching():
    """get_engine should return the same instance each time."""
    engine1 = db.get_engine()
    engine2 = db.get_engine()
    assert engine1 is engine2


# def test_missing_env_raises(monkeypatch):
#     """Missing DB_USER should raise RuntimeError."""
#     monkeypatch.setenv("DB_USER", "")
#     monkeypatch.setenv("DB_PASSWORD", "")
#     monkeypatch.setenv("DB_HOST", "")
#     monkeypatch.setenv("DB_NAME", "")

#     # reload db module to re-evaluate env checks
#     with pytest.raises(RuntimeError):
#         importlib.reload(db)
