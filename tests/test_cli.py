# tests/ui/test_cli.py

import pandas as pd
from dashboard_public_health.ui.cli.main_menu import MainMenu
from dashboard_public_health.ui.cli.filter_menu import FilterMenu
from dashboard_public_health.ui.cli.router import Menu
from dashboard_public_health.ui.cli.load_provenance import load_provenance_summary


# --------------------------------------------------------------------
# 1. MAIN MENU TESTS
# --------------------------------------------------------------------


def test_main_menu_registers_options():
    menu = MainMenu()

    assert "1" in menu.options  # ingest
    assert "2" in menu.options  # filter submenu
    assert "6" in menu.options  # logs
    assert "7" in menu.options  # provenance


def test_main_menu_ingest(monkeypatch):
    called = {}

    def fake_ingest(path):
        called["ok"] = True

    monkeypatch.setattr(
        "dashboard_public_health.application.ingestion_service.ingest_from_csv",
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
# 2. FILTER MENU — BASIC FILTER INPUT
# --------------------------------------------------------------------


def test_filter_menu_basic_filters(monkeypatch):
    inputs = iter(
        [
            "UK",  # country
            "Flu",  # disease
            "Viral",  # category
            "18-49",  # age_group
            "Both",  # gender
            "2000",  # year_from
            "2020",  # year_to
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    filters = FilterMenu.ask_basic_filters()

    assert filters["country"] == "UK"
    assert filters["disease"] == "Flu"
    assert filters["disease_category"] == "Viral"
    assert filters["age_group"] == "18-49"
    assert filters["gender"] == "Both"
    assert filters["year_from"] == 2000
    assert filters["year_to"] == 2020


# --------------------------------------------------------------------
# 3. FILTER MENU — APPLY FILTERS + CALL SERVICE
# --------------------------------------------------------------------


def test_filter_menu_apply_filters(monkeypatch):
    # Mock input sequence
    inputs = iter(
        [
            "UK",
            "Flu",
            "Viral",
            "18-49",
            "Both",
            "2000",
            "2020",  # basic filters
            "n",  # do not use advanced filters
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Mock returned dataframe
    fake_df = pd.DataFrame({"country": ["UK"], "year": [2020]})

    def fake_query(**kwargs):
        return fake_df

    monkeypatch.setattr(
        "dashboard_public_health.application.query_service.filter_records_with_connection",
        fake_query,
    )

    menu = FilterMenu()
    menu.apply_filters()

    assert isinstance(menu.last_df, pd.DataFrame)
    assert len(menu.last_df) == 1


# --------------------------------------------------------------------
# 4. ROUTER MENU — BASIC RUN FLOW
# --------------------------------------------------------------------


def test_router_menu_run(monkeypatch):
    called = {}

    def fake_exit():
        called["exit"] = True
        return True

    menu = Menu("Test", {"1": fake_exit})

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
