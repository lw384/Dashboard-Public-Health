# src/dashboard_public_health/ui/cli/session.py
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd

from dashboard_public_health.domain.models import FilterCriteria


@dataclass
class SessionContext:
    """
    Shared state across CLI menus.
    Stores last used filters, last DataFrame, last export path.
    """

    filters: Optional[FilterCriteria] = None
    last_df: Optional[pd.DataFrame] = None
    last_export_path: Optional[str] = None
