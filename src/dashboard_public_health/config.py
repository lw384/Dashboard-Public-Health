# src/dashboard_public_health/config.py
from pathlib import Path

# Path to the package directory: src/dashboard_public_health/
PACKAGE_ROOT = Path(__file__).resolve().parent

# Path to project root: the directory above "src"
PROJECT_ROOT = PACKAGE_ROOT.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

# Database file location
DB_PATH = DATA_DIR / "public_health.db"

# Default CSV for ingestion
DEFAULT_CSV = RAW_DATA_DIR / "Global_Health_Statistics.csv"
