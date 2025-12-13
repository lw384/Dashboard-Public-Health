# tests/ui/test_cli.py

import pandas as pd
from dashboard_public_health.ui.cli.main_menu import MainMenu
from dashboard_public_health.ui.cli.filter_menu import FilterMenu
from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.ui.cli.load_provenance import load_provenance_summary
from dashboard_public_health.ui.cli.crud_menu import CRUDMenu
from dashboard_public_health.ui.cli.export_menu import ExportMenu


# --------------------------------------------------------------------
# 1. MAIN MENU TESTS
# --------------------------------------------------------------------


def test_main_menu_registers_options():
    menu = MainMenu()

    assert "1" in menu.options  # ingest
    assert "2" in menu.options  # filter submenu
    assert "3" in menu.options  # export
    assert "6" in menu.options  # logs
    assert "7" in menu.options  # provenance


def test_main_menu_ingest(monkeypatch):
    called = {}

    def fake_ingest(path):
        called["ok"] = True

    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.main_menu.ingest_from_csv",
        fake_ingest,
    )

    menu = MainMenu()
    menu.ingest_data()

    assert called.get("ok") is True


def test_main_menu_provenance(monkeypatch):
    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.main_menu.load_provenance_summary",
        lambda: {"total_steps": 10},
    )

    menu = MainMenu()
    result = menu.show_provenance()

    assert result is None  # only prints, no return value


# --------------------------------------------------------------------
# 2. FILTER MENU — APPLY FILTERS + CALL SERVICE
# --------------------------------------------------------------------


def test_filter_menu_apply_filters(monkeypatch):
    # Mock input sequence for collect_filters (12 prompts)
    inputs = iter(
        [
            "UK",  # country
            "Flu",  # disease
            "Viral",  # disease_category
            "18-49",  # age_group
            "Both",  # gender
            "2000",  # year_from
            "2020",  # year_to
            "80",  # min_urbanization_rate
            "70",  # min_healthcare_access
            "4",  # min_hospital_beds
            "40000",  # min_income
            "0.5",  # min_education
        ]
    )
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs, ""))

    # Mock returned dataframe
    fake_df = pd.DataFrame({"country": ["UK"], "year": [2020]})
    captured = {}

    def fake_query(filters):
        captured["filters"] = filters
        return fake_df

    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.filter_menu.filter_records_with_connection",
        fake_query,
    )

    menu = FilterMenu()
    menu.apply_filters()

    assert isinstance(menu.last_df, pd.DataFrame)
    assert len(menu.last_df) == 1
    assert captured["filters"].country == "UK"
    assert captured["filters"].min_income == 40000.0


def test_filter_menu_export(monkeypatch, tmp_path):
    # filters (12 prompts) + export choice + filename
    inputs = iter([""] * 12 + ["csv", "filtered.csv"])
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs, ""))

    fake_df = pd.DataFrame({"country": ["UK"], "year": [2020]})

    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.filter_menu.filter_records_with_connection",
        lambda filters: fake_df,
    )
    # route export directory
    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.export_menu.OUTPUT_DIR", tmp_path
    )

    menu = FilterMenu()
    menu.apply_filters()

    assert (tmp_path / "filtered.csv").exists()


# --------------------------------------------------------------------
# 3. SUMMARY MENU — FILTER COLLECTION
# --------------------------------------------------------------------


def test_summary_menu_collect_filters(monkeypatch):
    inputs = iter(
        [
            "France",
            "COVID-19",
            "Viral",
            "50-64",
            "Female",
            "2020",
            "2022",
            "80",
            "70",
            "4",
            "50000",
            "0.6",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs, ""))

    fake_df = pd.DataFrame({"country": ["France"], "year": [2021]})
    captured = {}

    def fake_query(filters):
        captured["filters"] = filters
        return fake_df

    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.summary_menu.filter_records_with_connection",
        fake_query,
    )

    from dashboard_public_health.ui.cli.summary_menu import SummaryMenu

    smenu = SummaryMenu()
    df = smenu._load_filtered_df()

    assert not df.empty
    assert captured["filters"].country == "France"
    assert captured["filters"].min_healthcare_access == 70.0


# --------------------------------------------------------------------
# 4. ROUTER MENU — BASIC RUN FLOW
# --------------------------------------------------------------------


def test_router_menu_run(monkeypatch):
    called = {}

    def fake_exit():
        called["exit"] = True
        return True

    menu = Menu("Test", {"1": {"label": "Exit", "handler": fake_exit}})

    # simulate selecting option 1 then exit
    monkeypatch.setattr("builtins.input", lambda _: "1")

    menu.run()

    assert called.get("exit") is True


# --------------------------------------------------------------------
# 5. PROVENANCE LOADER TEST (NO FILE CASE)
# --------------------------------------------------------------------


def test_provenance_no_file(monkeypatch, tmp_path):
    f = tmp_path / "prov.jsonl"

    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.load_provenance.PROVENANCE_FILE", f
    )

    summary = load_provenance_summary()

    assert "error" in summary


# --------------------------------------------------------------------
# 6. CRUD MENU — BASIC OPERATIONS
# --------------------------------------------------------------------


def test_crud_menu_create(monkeypatch):
    inputs = iter(
        [
            "Japan",  # country
            "2022",  # year
            "Influenza",  # disease
            "Viral",  # category
            "7.0",  # prevalence
            "",  # incidence
            "",  # mortality
            "",  # population
            "",  # recovery
            "",  # dalys
            "",  # healthcare_access
            "",  # doctors
            "",  # beds
            "",  # income
            "",  # education
            "",  # urbanization
            "",  # age_group
            "",  # gender
            "",  # treatment
            "",  # source_file
        ]
    )
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs, ""))

    captured = {}

    def fake_insert(rec):
        captured["country"] = rec.country
        return 1

    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.crud_menu.insert_record", fake_insert
    )

    menu = CRUDMenu()
    menu.create_record()

    assert captured["country"] == "Japan"


def test_crud_menu_update_delete(monkeypatch):
    inputs = iter(
        [
            "1",  # update id
            "mortality_rate",
            "0.9",
            "1",  # delete id
        ]
    )
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs, ""))

    calls = {"update": None, "delete": None}

    def fake_update(record_id, updates):
        calls["update"] = (record_id, updates)
        return 1

    def fake_delete(record_id):
        calls["delete"] = record_id
        return 1

    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.crud_menu.update_record_by_id", fake_update
    )
    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.crud_menu.delete_record_by_id", fake_delete
    )

    menu = CRUDMenu()
    menu.update_record()
    menu.delete_record()

    assert calls["update"] == (1, {"mortality_rate": 0.9})
    assert calls["delete"] == 1


# --------------------------------------------------------------------
# 7. EXPORT MENU — FILTER + SAVE
# --------------------------------------------------------------------


def test_export_menu_exports_csv(monkeypatch, tmp_path):
    # filters (12 prompts) then filename prompt
    inputs = iter([""] * 12 + [""])  # blank filters and default filename
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs, ""))

    fake_df = pd.DataFrame({"country": ["UK"], "year": [2020]})
    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.export_menu.filter_records_with_connection",
        lambda filters: fake_df,
    )

    # direct ExportMenu constant to temp dir
    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.export_menu.OUTPUT_DIR", tmp_path
    )

    menu = ExportMenu()
    menu.export_csv()

    assert (tmp_path / "export.csv").exists()


# --------------------------------------------------------------------
# 8. SUMMARY MENU — EXPORT PROMPT
# --------------------------------------------------------------------


def test_summary_menu_export(monkeypatch, tmp_path):
    # filter inputs (12), export choice y, filename, press enter
    inputs = iter(
        [""] * 12  # filters none
        + ["y", "summary.csv", ""]  # export prompt, filename, press enter
    )
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs, ""))

    fake_df = pd.DataFrame({"country": ["France"], "year": [2021]})
    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.summary_menu.filter_records_with_connection",
        lambda filters: fake_df,
    )

    # patch plotting to no-op
    monkeypatch.setattr(
        "dashboard_public_health.application.visualization_service.plot_descriptive",
        lambda df: None,
    )
    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.summary_menu.plot_descriptive",
        lambda df: None,
    )

    # route export dir to tmp
    monkeypatch.setattr(
        "dashboard_public_health.ui.cli.export_menu.OUTPUT_DIR", tmp_path
    )

    from dashboard_public_health.ui.cli.summary_menu import SummaryMenu

    smenu = SummaryMenu()
    smenu.show_descriptive()

    assert (tmp_path / "summary.csv").exists()
