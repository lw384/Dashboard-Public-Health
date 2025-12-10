from dataclasses import dataclass
from typing import Optional, List


@dataclass
class HealthRecord:
    country: str
    year: int
    disease: str
    disease_category: str
    prevalence_rate: float
    incidence_rate: float
    mortality_rate: float
    population_affected: float
    recovery_rate: float
    dalys: float
    healthcare_access: float
    doctors_per_1000: float
    hospital_beds_per_1000: float
    per_capita_income: float
    education_index: float
    urbanization_rate: float
    age_group: str | None = None
    gender: str | None = None
    treatment_available: str | None = None


@dataclass
class FilterCriteria:
    country: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    disease: Optional[str] = None
    disease_category: Optional[str] = None
    age_group: Optional[str] = None
