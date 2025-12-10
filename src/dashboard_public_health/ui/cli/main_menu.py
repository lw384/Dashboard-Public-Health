# src/dashboard_public_health/ui/cli/main_menu.py

from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.ui.cli.filter_menu import FilterMenu
from dashboard_public_health.ui.cli.summary_menu import SummaryMenu
from dashboard_public_health.ui.cli.visualize_menu import VisualizationMenu
from dashboard_public_health.ui.cli.export_menu import ExportMenu
from dashboard_public_health.application.ingestion_service import ingest_from_csv
from dashboard_public_health.application.logger_service import read_last_logs
from dashboard_public_health.ui.cli.load_provenance import load_provenance_summary
from dashboard_public_health.config import DEFAULT_CSV


class MainMenu(Menu):
    def __init__(self):
        options = {
            "1": self.ingest_data,
            "2": self.open_filter_menu,
            # "3": self.open_summary_menu,
            # "4": self.open_visualization_menu,
            # "5": self.open_export_menu,
            "6": self.show_logs,
            "7": self.show_provenance,
        }
        super().__init__("Public Health Data Insights", options)

    # ---------------- Handlers ----------------

    def ingest_data(self):
        """Ingest data from CSV"""
        print(f"[Ingestion] Loading: {DEFAULT_CSV}")
        ingest_from_csv(DEFAULT_CSV)

    def open_filter_menu(self):
        """Filter data"""
        FilterMenu().run()

    def open_summary_menu(self):
        """Summary analysis"""
        SummaryMenu().run()

    def open_visualization_menu(self):
        """Visualize results"""
        VisualizationMenu().run()

    def open_export_menu(self):
        """Export results"""
        ExportMenu().run()

    def show_logs(self):
        """View log output"""
        logs = read_last_logs(50)
        print("\n".join(logs))

    def show_provenance(self):
        """View cleaning provenance"""
        summary = load_provenance_summary()
        print("\n=== Provenance Report ===")
        print(summary)
