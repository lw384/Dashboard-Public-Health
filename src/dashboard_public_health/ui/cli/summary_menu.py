# src/dashboard_public_health/ui/cli/summary_menu.py

from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.ui.cli.helpers import ask_filter_inputs
from dashboard_public_health.application.summary_service import (
    compute_summary,
    format_summary_report,
)
from dashboard_public_health.application.query_service import (
    filter_records_with_connection,
)


class SummaryMenu(Menu):
    def __init__(self):
        options = {
            "1": {
                "label": "Healthcare Policy Summary",
                "handler": lambda: self.run_summary("policy"),
            },
            "2": {
                "label": "Epidemiology Summary",
                "handler": lambda: self.run_summary("epidemiology"),
            },
            "3": {
                "label": "Machine Learning Prep Summary",
                "handler": lambda: self.run_summary("ml"),
            },
            "4": {
                "label": "Global Health Summary",
                "handler": lambda: self.run_summary("global"),
            },
            "0": {"label": "Back", "handler": self.exit_menu},
        }

        super().__init__("Summary Analysis", options)

    def run_summary(self, mode: str):
        print(f"\n=== Running {mode.capitalize()} Summary ===\n")

        filters = ask_filter_inputs()
        df = filter_records_with_connection(**filters)

        raw_summary = compute_summary(df, mode)
        formatted = format_summary_report(raw_summary, mode)

        print("\n=== SUMMARY RESULT ===\n")
        print(formatted)

        input("\nPress Enter to continue...")
        return False  # stay inside menu

    def exit_menu(self):
        return True
