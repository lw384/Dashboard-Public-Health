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
from dashboard_public_health.ui.cli.helpers import collect_filters
from dashboard_public_health.application.visualization_service import (
    plot_descriptive,
    plot_time_trends,
    plot_grouped,
    plot_corr,
)


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
        self.last_filters = None

    # ---------- Shared Filter Step ----------
    def _load_filtered_df(self):
        filters = collect_filters(defaults=self.last_filters)
        self.last_filters = filters
        df = filter_records_with_connection(filters)
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
        plot_descriptive(df)
        input("\nPress Enter to continue...")

    # ---------- Option 2 ----------
    def show_trends(self):
        df = self._load_filtered_df()
        if df is None:
            return
        summary = time_trend_summary(df)
        print("\n=== Time Trends ===\n")
        print(summary)
        plot_time_trends(df)
        input("\nPress Enter to continue...")

    # ---------- Option 3 ----------
    def show_grouped_stats(self):
        print("\n=== Grouped Statistics ===")
        df = self._load_filtered_df()
        if df is None:
            return

        # Ask user which column to group by
        col = input("Group by which column? (disease/country/age_group/etc.): ").strip()

        print(grouped_summary(df, col))
        plot_grouped(df, col)

        input("\nPress Enter to continue...")

    # ---------- Option 4 ----------
    def show_correlations(self):
        df = self._load_filtered_df()
        if df is None:
            return

        summary = correlation_summary(df)
        print("\n=== Correlation Analysis ===\n")
        print(summary)
        plot_corr(df)
        input("\nPress Enter to continue...")

    def exit_menu(self):
        print("Returning to main menu.")
        return True
