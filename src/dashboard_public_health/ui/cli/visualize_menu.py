# src/dashboard_public_health/ui/cli/visualize_menu.py

from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.ui.cli.helpers import ask_filter_inputs
from dashboard_public_health.application.query_service import filter_records_with_connection
from dashboard_public_health.application.visualization_service import (
    plot_trend,
    plot_grouped_bar,
)


class VisualizationMenu(Menu):
    def __init__(self):
        options = {
            "1": self.trend,
            "2": self.grouped_bar,
        }
        super().__init__("Visualization Tools", options)

    def _load_df(self):
        filters = ask_filter_inputs()
        return filter_records_with_connection(**filters)

    def trend(self):
        """Plot trend line"""
        df = self._load_df()
        plot_trend(df)

    def grouped_bar(self):
        """Plot grouped bar"""
        df = self._load_df()
        group_col = input("Group by (country / disease): ").strip() or "country"
        plot_grouped_bar(df, group_col)