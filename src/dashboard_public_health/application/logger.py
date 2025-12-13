from pathlib import Path
from dashboard_public_health.infrastructure.logger import LOG_FILE


def read_last_logs(n: int = 50) -> list[str]:
    """
    Return the last n lines from the application log file.
    """
    log_path = Path(LOG_FILE)

    if not log_path.exists():
        return ["[No log file found]"]

    lines = log_path.read_text().splitlines()

    # return only last N lines
    return lines[-n:] if len(lines) > n else lines
