import json
from pathlib import Path

PROVENANCE_FILE = Path("logs/provenance/clean_provenance.jsonl")


def load_provenance_summary():
    """Load provenance log and compute a simple summary dictionary."""
    if not PROVENANCE_FILE.exists():
        return {"error": "No provenance file found. Please run ingestion first."}

    steps = []
    with open(PROVENANCE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            steps.append(json.loads(line))

    summary = {
        "total_steps": len(steps),
        "steps": [],
        "total_rows_dropped": sum(s["rows_dropped"] for s in steps),
    }

    for s in steps:
        summary["steps"].append(
            {
                "step": s["step"],
                "before": s["before_rows"],
                "after": s["after_rows"],
                "dropped": s["rows_dropped"],
            }
        )

    return summary
