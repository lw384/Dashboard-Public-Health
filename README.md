# Dashboard-Public-Health

Python CLI for loading, cleaning, filtering, summarising, and visualising public health data (e.g., disease burden, access, resources). Data is ingested from CSV into SQLite, cleaned into a unified schema, and then explored through menus.

## Features
- Ingestion: load CSV (`data/raw/Global_Health_Statistics.csv` by default) into SQLite with schema init and duplicate protection.
- Cleaning pipeline: column normalisation, flexible auto-mapping, outlier caps, missing handling, type conversion, validation, dedup, and provenance logging to `logs/provenance/clean_provenance.jsonl`.
- Filtering: dynamic SQL WHERE builder supporting country, disease, year range, demographics, and threshold filters (urbanisation, healthcare access, beds, income, education).
- Summaries: descriptive stats, time trends, grouped means, correlation snippets; optional Matplotlib charts.
- Logging: function call logging to `logs/app.log`; provenance for each cleaning step.
- Export (WIP): CSV/JSON export functions exist; menu entry currently commented out.

## DataSets

https://www.kaggle.com/datasets/malaiarasugraj/global-health-statistics/data



## Project layout
```
src/dashboard_public_health/
  domain/           # Core models
  application/      # Cleaning, ingestion, querying, summaries, viz, logging
  infrastructure/   # CSV loader, SQLite helpers, logger setup, config paths
  ui/cli/           # Menu router, main menu, filter/summary/export helpers
data/               # Raw CSVs and SQLite DB location
  raw/              # Raw CSVs
logs/               # App logs and cleaning provenance
tests/              # Pytest suite
outputs/            # export csv
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
Main menu (after `poetry run start`):
```
===== Public Health Data Insights =====
1. Ingest data from CSV
2. Filter data
3. Export filtered dataset
4. Summary analysis
5. Manage records (CRUD)
6. View log output
7. View cleaning provenance
0. Exit
```

Menu highlights:
- Ingest: loads `data/raw/Global_Health_Statistics.csv` into SQLite (`data/public_health.db`) after cleaning.
- Filter: collect filters, show results, optional export of current dataframe.
- Export: CSV/JSON export; reuses last filtered dataframe if available.
- Summary: descriptive table (excluding id/year), time trends, grouped stats, correlations; can export current view data.
- CRUD: create/update/delete single records by id.
- Logs/Provenance: tail `logs/app.log` and view cleaning steps summary.

Notes:
- Filtering and summary menus ask for filters separately; they call the same query service underneath.
- Matplotlib uses `plt.show()`; in headless environments set an Agg backend or tweak to save figures.

## Screenshots

![](https://github.com/lw384/picx-images-hosting/raw/master/Figure_1_correlation.77e0kl9e5o.png)

![](https://github.com/lw384/picx-images-hosting/raw/master/Figure_1_group.9gx142u4mk.png)

![](https://github.com/lw384/picx-images-hosting/raw/master/Figure_1_trends.7zqw2bpzvv.png)

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
