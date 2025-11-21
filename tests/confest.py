"""Test for local varibles"""

import os
import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def db_env():
    """Return env vars if all present; otherwise skip integration tests."""
    required = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
    missing = [k for k in required if not os.getenv(k)]

    if missing:
        pytest.skip(f"Skipping DB integration tests, missing: {missing}")

    return {k: os.getenv(k) for k in required}
