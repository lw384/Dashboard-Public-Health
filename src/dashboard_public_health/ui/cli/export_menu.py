# src/dashboard_public_health/ui/cli/export_menu.py

import pandas as pd
from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.ui.cli.helpers import ask_filter_inputs
from dashboard_public_health.application.query_service import (
    filter_records_with_connection,
)


class ExportMenu(Menu):
    def __init__(self):
        options = {
            "1": self.export_csv,
            "2": self.export_json,
        }
        super().__init__("Export Data", options)

    def _load_df(self):
        filters = ask_filter_inputs()
        return filter_records_with_connection(**filters)

    def export_csv(self):
        """Export filtered data to CSV"""
        df = self._load_df()
        df.to_csv("export.csv", index=False)
        print("Saved to export.csv")

    def export_json(self):
        """Export filtered data to JSON"""
        df = self._load_df()
        df.to_json("export.json", orient="records")
        print("Saved to export.json")
