# src/dashboard_public_health/ui/cli/filter_menu.py

from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.application.query_service import (
    filter_records_with_connection,
)

MAX_DISPLAY_ROWS = 50


class FilterMenu(Menu):
    """
    A submenu that allows users to apply filtering conditions.
    Inherits from Menu so it can be opened by MainMenu.
    """

    def __init__(self):
        options = {
            "1": self.apply_filters,
            "0": self.exit_menu,
        }
        super().__init__("Filter Records", options)
        self.last_df = None  # store last filtered results for summary / visualization

    # ---------------------------
    # Filtering Logic
    # ---------------------------

    @staticmethod
    def ask_basic_filters():
        print("\n--- Basic Filters ---")
        country = input("Country (blank = none): ").strip() or None
        disease = input("Disease (blank = none): ").strip() or None
        category = input("Disease category (blank = none): ").strip() or None
        age_group = (
            input("Age group (0-17 / 18-49 / 50-64 / 65+ / Unknown): ").strip() or None
        )
        gender = input("Gender (Male/Female/Both, blank = none): ").strip() or None

        year_from = input("Year from (blank=none): ").strip()
        year_from = int(year_from) if year_from.isdigit() else None

        year_to = input("Year to (blank=none): ").strip()
        year_to = int(year_to) if year_to.isdigit() else None

        return {
            "country": country,
            "disease": disease,
            "disease_category": category,
            "age_group": age_group,
            "gender": gender,
            "year_from": year_from,
            "year_to": year_to,
        }

    @staticmethod
    def ask_advanced_filters():
        print("\n--- Advanced Filters (Optional) ---")

        def read_float(prompt):
            val = input(prompt).strip()
            return float(val) if val.replace(".", "", 1).isdigit() else None

        return {
            "min_urbanization_rate": read_float("Min urbanization rate (%): "),
            "min_healthcare_access": read_float("Min healthcare access (%): "),
            "min_hospital_beds": read_float("Min hospital beds per 1000: "),
            "min_income": read_float("Min per capita income: "),
            "min_education": read_float("Min education index: "),
        }

    def apply_filters(self):
        """Collect filter options and run filtering."""
        print("\nCollecting filter conditions…")

        filters = self.ask_basic_filters()

        use_advanced = input("Apply advanced filters? (y/n): ").strip().lower()
        if use_advanced == "y":
            filters.update(self.ask_advanced_filters())

        df = filter_records_with_connection(**filters)
        self.last_df = df

        print(f"\nFiltered {len(df)} rows.")
        
        total = len(df)
        n_show = min(total, MAX_DISPLAY_ROWS)
        if total > MAX_DISPLAY_ROWS:
            print(f"(Showing only first {MAX_DISPLAY_ROWS} rows)\n")
        else:
            print(f"(Showing all {n_show} rows)\n")

        if total > 0:
            print(df.head(n_show))
        else:
            print("No results match your filters.")

    def exit_menu(self):
        print("Returning to main menu.")
        return True
