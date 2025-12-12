# Dashboard-Public-Health

Python CLI for loading, cleaning, filtering, summarising, and visualising public health data (e.g., disease burden, access, resources). Data is ingested from CSV into SQLite, cleaned into a unified schema, and then explored through menus.

## Features
- Ingestion: load CSV (`data/raw/Global_Health_Statistics.csv` by default) into SQLite with schema init and duplicate protection.
- Cleaning pipeline: column normalisation, flexible auto-mapping, outlier caps, missing handling, type conversion, validation, dedup, and provenance logging to `logs/provenance/clean_provenance.jsonl`.
- Filtering: dynamic SQL WHERE builder supporting country, disease, year range, demographics, and threshold filters (urbanisation, healthcare access, beds, income, education).
- Summaries: descriptive stats, time trends, grouped means, correlation snippets; optional Matplotlib charts.
- Logging: function call logging to `logs/app.log`; provenance for each cleaning step.
- Export (WIP): CSV/JSON export functions exist; menu entry currently commented out.

## Project layout
```
src/dashboard_public_health/
  domain/           # Core models
  application/      # Cleaning, ingestion, querying, summaries, viz, logging
  infrastructure/   # CSV loader, SQLite helpers, logger setup, config paths
  ui/cli/           # Menu router, main menu, filter/summary/export helpers
data/               # Raw CSVs and SQLite DB location
logs/               # App logs and cleaning provenance
tests/              # Pytest suite
```

## Quickstart
Requirements: Python >= 3.14, Poetry (or use `pip install -e .` with deps from `pyproject.toml`).

```bash
poetry install
# Run CLI
poetry run start
```

If you prefer plain python:
```bash
pip install -e .
python -m dashboard_public_health
```

## Usage (CLI)
Main menu options:
- Ingest data from CSV: loads `data/raw/Global_Health_Statistics.csv` into SQLite (`data/public_health.db`) after cleaning.
- Filter data: interactively collect filters and show matching rows.
- Summary analysis: descriptive stats, time trends, grouped stats, correlations (+ Matplotlib plots).
- View log output: tail of `logs/app.log`.
- View cleaning provenance: aggregated steps/rows dropped from the cleaning pipeline.

Notes:
- Filtering and summary menus ask for filters separately; they call the same query service underneath.
- Matplotlib uses `plt.show()`; in headless environments set an Agg backend or tweak to save figures.

## Configuration
- Paths are defined in `src/dashboard_public_health/config.py` (project root, data dir, DB path, default CSV).
- Logging: `logs/app.log`; cleaning provenance: `logs/provenance/clean_provenance.jsonl`.

## Testing
```bash
poetry run pytest
```

## Implementation highlights
- Cleaning pipeline in `application/clean.py` with provenance decorator for each step.
- Flexible column mapping (`application/auto_mapper.py`) to tolerate varied CSV headers.
- SQLite helpers (`infrastructure/db.py`) always read DB path from `config.DB_PATH` to ease testing/patching.

## Known gaps / WIP
- CLI export menu exists (`ui/cli/export_menu.py`) but is not wired into the main menu.
- `ui/cli/visualize_menu.py` is a placeholder; visualisation currently lives under summary options.
- No external API/data source ingestion beyond CSV yet.***
