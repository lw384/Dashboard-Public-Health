# ui/cli.py
from dashboard_public_health.application.exploration_service import filter_and_summarise
from dashboard_public_health.application.ingestion_service import ingest_from_csv
from pathlib import Path

from dashboard_public_health.config import DEFAULT_CSV


def run_cli():
    while True:
        print("1. 加载数据并写入数据库")
        print("2. 按条件过滤并查看统计")
        print("0. 退出")
        choice = input("请选择: ")

        if choice == "1":
            ingest_from_csv(DEFAULT_CSV)
        elif choice == "2":
            country = input("国家（可留空）: ").strip() or None
            start = input("起始年份（可留空）: ").strip()
            end = input("结束年份（可留空）: ").strip()
            start_year = int(start) if start else None
            end_year = int(end) if end else None
            summary, grouped = filter_and_summarise(country, start_year, end_year)
            print("总体统计:", summary)
            print("按国家分组统计:")
            for c, stats in grouped.items():
                print(c, stats)
        elif choice == "0":
            break
