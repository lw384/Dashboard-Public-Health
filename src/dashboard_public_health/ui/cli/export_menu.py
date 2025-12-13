# src/dashboard_public_health/ui/cli/export_menu.py

import os
import pandas as pd
from pathlib import Path
from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.ui.cli.helpers import collect_filters
from dashboard_public_health.application.query import (
    filter_records_with_connection,
)

OUTPUT_DIR = Path("outputs")


class ExportMenu(Menu):
    def __init__(self):
        options = {
            "1": {"label": "Export CSV", "handler": self.export_csv},
            "2": {"label": "Export JSON", "handler": self.export_json},
            "0": {"label": "Back", "handler": self.exit_menu},
        }
        super().__init__("Export Data", options)

    def _load_df(self):
        try:
            filters = collect_filters()
        except KeyboardInterrupt:
            print("\n[export] Cancelled.")
            return None
        return filter_records_with_connection(filters)

    @staticmethod
    def _ensure_output_dir():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _prompt_filename(default_name: str):
        name = input(f"Output filename (default={default_name}): ").strip()
        return name or default_name

    def _export_df(self, df: pd.DataFrame, filename: str, fmt: str):
        self._ensure_output_dir()
        path = OUTPUT_DIR / filename
        if fmt == "csv":
            df.to_csv(path, index=False)
        elif fmt == "json":
            df.to_json(path, orient="records")
        print(f"Saved to {path}")

    def export_csv(self):
        """Export filtered data to CSV"""
        df = self._load_df()
        if df is None:
            return
        default_name = "export.csv"
        filename = self._prompt_filename(default_name)
        self._export_df(df, filename, "csv")

    def export_json(self):
        """Export filtered data to JSON"""
        df = self._load_df()
        if df is None:
            return
        default_name = "export.json"
        filename = self._prompt_filename(default_name)
        self._export_df(df, filename, "json")

    def exit_menu(self):
        print("Returning to main menu.")
        return True
