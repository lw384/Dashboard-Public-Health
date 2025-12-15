import functools
import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


def get_logger():
    logger = logging.getLogger("dashboard_public_health")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        fh = logging.FileHandler(LOG_FILE)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


logger = get_logger()


def log_action(func):
    """Decorator to log function calls, parameters, and results."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"CALL: {func.__name__} args={args} kwargs={kwargs}")

        result = func(*args, **kwargs)

        # If result is a DataFrame, log its row count
        try:
            if hasattr(result, "shape"):
                logger.info(
                    f"RETURN: {func.__name__} -> DataFrame(rows={result.shape[0]})"
                )
            else:
                logger.info(f"RETURN: {func.__name__} -> {result}")
        except Exception:
            logger.info(f"RETURN: {func.__name__}")

        return result

    return wrapper
