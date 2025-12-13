# src/dashboard_public_health/ui/cli/summary_menu.py

from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.application.summary import (
    descriptive_summary,
    time_trend_summary,
    grouped_summary,
    correlation_summary,
)
from dashboard_public_health.application.query import (
    filter_records_with_connection,
)
from dashboard_public_health.ui.cli.helpers import collect_filters
from dashboard_public_health.application.visualization import (
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
        if filters is None:
            return None
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
        numeric = df.select_dtypes(include="number")
        table = numeric.describe().T.round(2)
        print("\n=== Descriptive Summary (table) ===\n")
        print(table.to_string())
        self._maybe_export(df, default_name="descriptive.csv")
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
        self._maybe_export(df, default_name="time_trends.csv")
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

        self._maybe_export(df, default_name=f"grouped_{col}.csv")
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
        self._maybe_export(df, default_name="correlations.csv")
        input("\nPress Enter to continue...")

    def exit_menu(self):
        print("Returning to main menu.")
        return True

    # ---------- Export helper ----------
    def _maybe_export(self, df, default_name="export.csv"):
        choice = input("Export this filtered dataset? (y/n): ").strip().lower()
        if choice != "y":
            return
        from dashboard_public_health.ui.cli.export_menu import ExportMenu

        exporter = ExportMenu()
        filename = exporter._prompt_filename(default_name)
        exporter._ensure_output_dir()
        exporter._export_df(df, filename, "csv")
