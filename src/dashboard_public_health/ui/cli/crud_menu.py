# src/dashboard_public_health/ui/cli/crud_menu.py
from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.domain.models import HealthRecord
from dashboard_public_health.infrastructure.db import (
    insert_record,
    update_record_by_id,
    delete_record_by_id,
)


def _read_str(prompt):
    val = input(prompt).strip()
    return val or None


def _read_int(prompt):
    val = input(prompt).strip()
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None


def _read_float(prompt):
    val = input(prompt).strip()
    if not val:
        return None
    try:
        return float(val)
    except ValueError:
        return None


class CRUDMenu(Menu):
    """CLI for basic CRUD operations on records."""

    def __init__(self):
        options = {
            "1": {"label": "Create record", "handler": self.create_record},
            "2": {"label": "Update record by ID", "handler": self.update_record},
            "3": {"label": "Delete record by ID", "handler": self.delete_record},
            "0": {"label": "Back", "handler": self.exit_menu},
        }
        super().__init__("Manage Records", options)

    def create_record(self):
        print("\n--- Create Record ---")
        data = {
            "country": _read_str("Country (required): "),
            "year": _read_int("Year (required): "),
            "disease": _read_str("Disease (required): "),
            "disease_category": _read_str("Disease category: "),
            "prevalence_rate": _read_float("Prevalence rate: "),
            "incidence_rate": _read_float("Incidence rate: "),
            "mortality_rate": _read_float("Mortality rate: "),
            "population_affected": _read_float("Population affected: "),
            "recovery_rate": _read_float("Recovery rate: "),
            "dalys": _read_float("DALYs: "),
            "healthcare_access": _read_float("Healthcare access: "),
            "doctors_per_1000": _read_float("Doctors per 1000: "),
            "hospital_beds_per_1000": _read_float("Hospital beds per 1000: "),
            "per_capita_income": _read_float("Per capita income: "),
            "education_index": _read_float("Education index: "),
            "urbanization_rate": _read_float("Urbanization rate: "),
            "age_group": _read_str("Age group: "),
            "gender": _read_str("Gender: "),
            "treatment_available": _read_str("Treatment available: "),
            "source_file": _read_str("Source file: "),
        }

        if not data["country"] or data["year"] is None or not data["disease"]:
            print("Country, Year, and Disease are required.")
            return

        record = HealthRecord.from_dict(data)
        insert_record(record)
        print("Record created.")

    def update_record(self):
        print("\n--- Update Record ---")
        record_id = _read_int("Record ID to update: ")
        if record_id is None:
            print("Invalid ID.")
            return

        field = _read_str("Field to update (e.g., mortality_rate): ")
        if not field:
            print("Field name is required.")
            return

        value_str = input("New value: ").strip()
        value: object = value_str
        # attempt numeric casts
        try:
            if "." in value_str:
                value = float(value_str)
            else:
                value = int(value_str)
        except ValueError:
            value = value_str or None

        updated = update_record_by_id(record_id, {field: value})
        if updated:
            print("Record updated.")
        else:
            print("No record updated (check ID).")

    def delete_record(self):
        print("\n--- Delete Record ---")
        record_id = _read_int("Record ID to delete: ")
        if record_id is None:
            print("Invalid ID.")
            return
        deleted = delete_record_by_id(record_id)
        if deleted:
            print("Record deleted.")
        else:
            print("No record deleted (check ID).")

    def exit_menu(self):
        print("Returning to main menu.")
        return True
