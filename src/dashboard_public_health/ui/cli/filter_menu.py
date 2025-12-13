# src/dashboard_public_health/ui/cli/filter_menu.py

from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.application.query import (
    filter_records_with_connection,
)
from dashboard_public_health.ui.cli.helpers import collect_filters
from dashboard_public_health.ui.cli.export_menu import ExportMenu

MAX_DISPLAY_ROWS = 50


class FilterMenu(Menu):
    """
    A submenu that allows users to apply filtering conditions.
    Inherits from Menu so it can be opened by MainMenu.
    """

    def __init__(self):
        options = {
            "1": {"label": "Apply filters", "handler": self.apply_filters},
            "0": {"label": "Back", "handler": self.exit_menu},
        }
        super().__init__("Filter Records", options)
        self.last_df = None  # store last filtered results for summary / visualization
        self.last_filters = None  # persist filters across runs

    # ---------------------------
    # Filtering Logic
    # ---------------------------

    def apply_filters(self):
        """Collect filter options and run filtering."""
        print("\nCollecting filter conditions…")

        filters = collect_filters(defaults=self.last_filters)
        if filters is None:
            return
        self.last_filters = filters

        df = filter_records_with_connection(filters)
        self.last_df = df

        print(f"\nFiltered {len(df)} rows.")

        total = len(df)
        n_show = min(total, MAX_DISPLAY_ROWS)
        if total > MAX_DISPLAY_ROWS:
            print(f"(Showing only first {MAX_DISPLAY_ROWS} rows)\n")
        else:
            print(f"(Showing all {n_show} rows)\n")

        if total > 0:
            print(df.head(n_show))
            self._maybe_export(df)
        else:
            print("No results match your filters.")

    def exit_menu(self):
        print("Returning to main menu.")
        return True

    def _maybe_export(self, df):
        choice = input("Export results? (csv/json/n): ").strip().lower()
        if choice not in {"csv", "json"}:
            return
        exporter = ExportMenu()
        default_name = f"filtered.{choice}"
        filename = exporter._prompt_filename(default_name)
        exporter._ensure_output_dir()
        exporter._export_df(df, filename, choice)
