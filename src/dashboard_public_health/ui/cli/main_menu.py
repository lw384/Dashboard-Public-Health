# src/dashboard_public_health/ui/cli/main_menu.py

from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.ui.cli.filter_menu import FilterMenu
from dashboard_public_health.ui.cli.summary_menu import SummaryMenu
from dashboard_public_health.ui.cli.export_menu import ExportMenu
from dashboard_public_health.application.ingestion import ingest_from_csv
from dashboard_public_health.application.logger import read_last_logs
from dashboard_public_health.ui.cli.load_provenance import load_provenance_summary
from dashboard_public_health.ui.cli.crud_menu import CRUDMenu
from dashboard_public_health.config import DEFAULT_CSV
from dashboard_public_health.ui.cli.session import SessionContext


class MainMenu(Menu):
    def __init__(self):
        self.session = SessionContext()
        options = {
            "1": {"label": "Ingest data from CSV", "handler": self.ingest_data},
            "2": {"label": "Filter data", "handler": self.open_filter_menu},
            "3": {"label": "Export filtered dataset", "handler": self.open_export_menu},
            "4": {"label": "Summary analysis", "handler": self.open_summary_menu},
            "5": {"label": "Manage records (CRUD)", "handler": self.open_crud_menu},
            "6": {"label": "View log output", "handler": self.show_logs},
            "7": {"label": "View cleaning provenance", "handler": self.show_provenance},
            "0": {"label": "Exit", "handler": self.exit_menu},
        }
        super().__init__("Public Health Data Insights", options)

    # ---------------- Handlers ----------------

    def ingest_data(self):
        """Ingest data from CSV"""
        print(f"[Ingestion] Loading: {DEFAULT_CSV}")
        ingest_from_csv(DEFAULT_CSV)

    def open_filter_menu(self):
        """Filter data"""
        FilterMenu(session=self.session).run()

    def open_summary_menu(self):
        """Summary analysis"""
        SummaryMenu(session=self.session).run()

    def open_visualization_menu(self):
        """Visualize results"""
        VisualizationMenu().run()

    def open_export_menu(self):
        """Export results"""
        ExportMenu(session=self.session).run()

    def show_logs(self):
        """View log output"""
        logs = read_last_logs(50)
        print("\n".join(logs))

    def show_provenance(self):
        """View cleaning provenance"""
        summary = load_provenance_summary()
        print("\n=== Provenance Report ===")
        print(summary)

    def open_crud_menu(self):
        """Manage records CRUD"""
        CRUDMenu().run()

    def exit_menu(self):
        print("Exiting program.")
        return True
