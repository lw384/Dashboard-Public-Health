import json
import pandas as pd
from dashboard_public_health.application.provenance import with_provenance


def test_provenance_file_created(tmp_path, monkeypatch):
    """Ensure provenance decorator creates JSONL & logger entry."""

    # Redirect provenance output to a temporary directory
    fake_dir = tmp_path / "prov"
    fake_file = fake_dir / "clean_provenance.jsonl"

    monkeypatch.setattr(
        "dashboard_public_health.application.provenance.PROVENANCE_DIR", str(fake_dir)
    )
    monkeypatch.setattr(
        "dashboard_public_health.application.provenance.PROVENANCE_FILE", str(fake_file)
    )

    # Dummy cleaning step
    @with_provenance("dummy_step")
    def dummy_clean(df):
        return df[df["value"] > 1]

    df = pd.DataFrame({"value": [0, 2, 3]})
    result = dummy_clean(df)

    # 1) Ensure rows were cleaned correctly
    assert len(result) == 2

    # 2) Provenance file created
    assert fake_file.exists()

    # 3) Provenance entry is correct
    with open(fake_file, "r") as f:
        lines = f.readlines()

    assert len(lines) == 1

    entry = json.loads(lines[0])
    assert entry["step"] == "dummy_step"
    assert entry["before_rows"] == 3
    assert entry["after_rows"] == 2
    assert entry["rows_dropped"] == 1
