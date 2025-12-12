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
    source_file: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "HealthRecord":
        """Construct from a dictionary with keys matching the internal schema."""
        return cls(
            country=data.get("country"),
            year=int(data.get("year")) if data.get("year") is not None else None,
            disease=data.get("disease"),
            disease_category=data.get("disease_category"),
            prevalence_rate=data.get("prevalence_rate"),
            incidence_rate=data.get("incidence_rate"),
            mortality_rate=data.get("mortality_rate"),
            population_affected=data.get("population_affected"),
            recovery_rate=data.get("recovery_rate"),
            dalys=data.get("dalys"),
            healthcare_access=data.get("healthcare_access"),
            doctors_per_1000=data.get("doctors_per_1000"),
            hospital_beds_per_1000=data.get("hospital_beds_per_1000"),
            per_capita_income=data.get("per_capita_income"),
            education_index=data.get("education_index"),
            urbanization_rate=data.get("urbanization_rate"),
            age_group=data.get("age_group"),
            gender=data.get("gender"),
            treatment_available=data.get("treatment_available"),
            source_file=data.get("source_file"),
        )

    def to_db_tuple(self):
        """
        Tuple aligned with INSERT order in infrastructure/db.py
        """
        return (
            self.country,
            self.year,
            self.disease,
            self.disease_category,
            self.prevalence_rate,
            self.incidence_rate,
            self.mortality_rate,
            self.population_affected,
            self.recovery_rate,
            self.dalys,
            self.healthcare_access,
            self.doctors_per_1000,
            self.hospital_beds_per_1000,
            self.per_capita_income,
            self.education_index,
            self.urbanization_rate,
            self.age_group,
            self.gender,
            self.treatment_available,
            self.source_file,
        )

    def to_dict(self):
        return self.__dict__.copy()

@dataclass
class FilterCriteria:
    country: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    disease: Optional[str] = None
    disease_category: Optional[str] = None
    age_group: Optional[str] = None
    gender: Optional[str] = None
    min_urbanization_rate: Optional[float] = None
    min_healthcare_access: Optional[float] = None
    min_hospital_beds: Optional[float] = None
    min_income: Optional[float] = None
    min_education: Optional[float] = None
