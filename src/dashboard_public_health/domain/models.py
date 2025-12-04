# domain/models.py
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Record:
    country: str
    year: int
    metric_name: str
    value: float


@dataclass
class FilterCriteria:
    country: str | None = None
    start_year: int | None = None
    end_year: int | None = None


@dataclass
class SummaryStats:
    count: int
    mean: float
    minimum: float
    maximum: float
