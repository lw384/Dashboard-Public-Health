# src/dashboard_public_health/ui/cli/summary_menu.py

from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.ui.cli.helpers import ask_filter_inputs

# from dashboard_public_health.application.summary_service import (
#     policy_summary,
#     epidemiology_summary,
#     ml_prep_summary,
#     global_health_summary,
# )


class SummaryMenu(Menu):
    def __init__(self):
        options = {
            "1": self.policy,
            "2": self.epidemiology,
            "3": self.machine_learning,
            "4": self.global_health,
        }
        super().__init__("Summary Statistics", options)

    def _run_summary(self, func):
        filters = ask_filter_inputs()
        summary = func(**filters)
        print("\n=== Summary ===")
        for k, v in summary.items():
            print(f"{k}: {v}")

    def policy(self):
        """Healthcare Policy Analysis"""
        self._run_summary(policy_summary)

    def epidemiology(self):
        """Epidemiological Studies"""
        self._run_summary(epidemiology_summary)

    def machine_learning(self):
        """Machine Learning Preparation"""
        self._run_summary(ml_prep_summary)

    def global_health(self):
        """Global Health Research"""
        self._run_summary(global_health_summary)
