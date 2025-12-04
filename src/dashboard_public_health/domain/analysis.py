from statistics import mean
from collections import defaultdict


def calculate_summary(records: list[Record]) -> SummaryStats:
    values = [r.value for r in records]
    return SummaryStats(
        count=len(values),
        mean=mean(values) if values else 0.0,
        minimum=min(values) if values else 0.0,
        maximum=max(values) if values else 0.0,
    )


def group_by_country(records: list[Record]):
    groups = defaultdict(list)
    for r in records:
        groups[r.country].append(r.value)
    # 返回 {country: SummaryStats}
    return {
        country: SummaryStats(
            count=len(vals),
            mean=mean(vals),
            minimum=min(vals),
            maximum=max(vals),
        )
        for country, vals in groups.items()
    }
