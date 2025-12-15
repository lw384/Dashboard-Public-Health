# provenance.py
import json
import os
from datetime import datetime
from functools import wraps
import pandas as pd

from dashboard_public_health.infrastructure.logger import logger  # import shared logger

PROVENANCE_DIR = "logs/provenance"
PROVENANCE_FILE = os.path.join(PROVENANCE_DIR, "clean_provenance.jsonl")


def _ensure_dir():
    os.makedirs(PROVENANCE_DIR, exist_ok=True)


def _write_jsonl(entry: dict):
    _ensure_dir()
    with open(PROVENANCE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _log_to_logger(entry: dict):
    """Send provenance info into main logger."""
    logger.info(
        f"PROVENANCE | step={entry['step']} "
        f"rows_before={entry['before_rows']} "
        f"rows_after={entry['after_rows']} "
        f"dropped={entry['rows_dropped']}"
    )


def with_provenance(step_name: str):
    """
    Decorator for DF → DF cleaning functions.
    Records provenance to:
        - provenance JSONL file
        - logger (app.log)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(df: pd.DataFrame, *args, **kwargs):

            before_rows = len(df)
            before_cols = list(df.columns)

            result = func(df, *args, **kwargs)

            after_rows = len(result)
            after_cols = list(result.columns)

            entry = {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "step": step_name,
                "before_rows": before_rows,
                "after_rows": after_rows,
                "rows_dropped": before_rows - after_rows,
                "before_cols": before_cols,
                "after_cols": after_cols,
            }

            # write provenance file
            _write_jsonl(entry)

            # also write to logger
            _log_to_logger(entry)

            return result

        return wrapper

    return decorator
