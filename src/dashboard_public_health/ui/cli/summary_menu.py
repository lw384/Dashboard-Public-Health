# src/dashboard_public_health/ui/cli/summary_menu.py

from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.application.summary_service import (
    descriptive_summary,
    time_trend_summary,
    grouped_summary,
    correlation_summary,
)
from dashboard_public_health.application.query_service import (
    filter_records_with_connection,
)
from dashboard_public_health.ui.cli.helpers import ask_filter_inputs


class SummaryMenu(Menu):

    def __init__(self):
        options = {
            "1": {
                "label": "View descriptive summary",
                "handler": self.show_descriptive,
            },
            "2": {"label": "View time trends", "handler": self.show_trends},
            "3": {
                "label": "View grouped statistics",
                "handler": self.show_grouped_stats,
            },
            "4": {"label": "View correlations", "handler": self.show_correlations},
            "0": {"label": "Back", "handler": self.exit_menu},
        }

        super().__init__(
            title="Summary Analysis",
            options=options,
            description="This feature generates insights based on your current filters.",
        )

    # ---------- Shared Filter Step ----------
    def _load_filtered_df(self):
        filters = ask_filter_inputs()
        df = filter_records_with_connection(**filters)
        if df.empty:
            print("\n⚠ No data matches your filters.\n")
            return None
        return df

    # ---------- Option 1 ----------
    def show_descriptive(self):
        df = self._load_filtered_df()
        if df is None:
            return
        summary = descriptive_summary(df)
        print("\n=== Descriptive Summary ===\n")
        print(summary)
        input("\nPress Enter to continue...")

    # ---------- Option 2 ----------
    def show_trends(self):
        df = self._load_filtered_df()
        if df is None:
            return
        summary = time_trend_summary(df)
        print("\n=== Time Trends ===\n")
        print(summary)
        input("\nPress Enter to continue...")

    # ---------- Option 3 ----------
    def show_grouped_stats(self):
        df = self._load_filtered_df()
        if df is None:
            return

        group_col = input("Group by (country/disease/age_group/gender): ").strip()
        summary = grouped_summary(df, group_col)

        print("\n=== Grouped Statistics ===\n")
        print(summary)
        input("\nPress Enter to continue...")

    # ---------- Option 4 ----------
    def show_correlations(self):
        df = self._load_filtered_df()
        if df is None:
            return

        summary = correlation_summary(df)
        print("\n=== Correlation Analysis ===\n")
        print(summary)
        input("\nPress Enter to continue...")

    def exit_menu(self):
        print("Returning to main menu.")
        return True
