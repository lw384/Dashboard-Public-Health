# domain/rules.py
from .models import Record
from typing import Iterable
from .models import Record, FilterCriteria


def from_row(row) -> Record:
    # row 可以是 pandas Series
    return Record(
        country=str(row["country"]).strip(),
        year=int(row["year"]),
        metric_name=str(row["metric_name"]),
        value=float(row["value"]),
    )


def apply_filter(records: Iterable[Record], criteria: FilterCriteria):
    result = []
    for r in records:
        if criteria.country and r.country != criteria.country:
            continue
        if criteria.start_year and r.year < criteria.start_year:
            continue
        if criteria.end_year and r.year > criteria.end_year:
            continue
        result.append(r)
    return result
