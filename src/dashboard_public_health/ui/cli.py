# ui/cli.py
from dashboard_public_health.application.ingestion_service import ingest_from_csv
from dashboard_public_health.application.query_service import (
    filter_records_with_connection,
    summarise_filtered_data,
)
from dashboard_public_health.config import DEFAULT_CSV
from dashboard_public_health.application.visualization_service import (
    plot_trend,
    plot_grouped_bar,
)
from dashboard_public_health.application.logger_service import read_last_logs


def run_cli():
    while True:
        print("\n================= Public Health Data Insights =================")
        print("1. Ingest data from CSV")
        print("2. Filter records")
        print("3. View summary statistics")
        print("4. View grouped statistics")
        print("5. Show first 10 filtered rows")
        print("6. Plot trend chart")
        print("7. Plot grouped bar chart")
        print("8. View log file")
        print("0. Exit")
        print("================================================================")

        choice = input("Select an option: ").strip()

        if choice == "0":
            print("Exiting. Goodbye!")
            break

        # ------------------- Ingestion -------------------
        elif choice == "1":
            print(f"[Ingestion] Loading data from: {DEFAULT_CSV}")
            ingest_from_csv(DEFAULT_CSV)

        # ------------------- Filtering -------------------
        elif choice == "2":
            country, start_date, end_date, age_group = ask_filter_inputs()

            df = filter_records_with_connection(
                country=country,
                start_date=start_date,
                end_date=end_date,
                age_group=age_group,
            )

            print(f"\nFiltered records count: {len(df)}")
            print(df.head(10))

        # ------------------- Summary statistics -------------------
        elif choice == "3":
            country, start_date, end_date, age_group = ask_filter_inputs()

            summary = summarise_filtered_data(
                country=country,
                start_date=start_date,
                end_date=end_date,
                age_group=age_group,
            )

            print("\n=== Summary Statistics ===")
            for key, value in summary.items():
                print(f"{key}: {value}")

        # ------------------- Grouped statistics -------------------
        elif choice == "4":
            country, start_date, end_date, age_group = ask_filter_inputs()

            grouped = group_statistics(
                country=country,
                start_date=start_date,
                end_date=end_date,
                age_group=age_group,
            )

            print("\n=== Grouped Statistics (by country) ===")
            for group, stats in grouped.items():
                print(f"\n{group}:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")

        # ------------------- Display first rows -------------------
        elif choice == "5":
            country, start_date, end_date, age_group = ask_filter_inputs()

            df = filter_records_with_connection(
                country=country,
                start_date=start_date,
                end_date=end_date,
                age_group=age_group,
            )
            print(df.head(10))
        elif choice == "6":
            country, start_date, end_date, age_group = ask_filter_inputs()
            df = filter_records_with_connection(
                country=country,
                start_date=start_date,
                end_date=end_date,
                age_group=age_group,
            )
            plot_trend(df)

        elif choice == "7":
            country, start_date, end_date, age_group = ask_filter_inputs()
            df = filter_records_with_connection(
                country=country,
                start_date=start_date,
                end_date=end_date,
                age_group=age_group,
            )
            group_col = input("Group by (country/age_group): ").strip() or "country"
            plot_grouped_bar(df, group_col)
        elif choice == "8":
            num = input(
                "How many log lines would you like to view? (default 50): "
            ).strip()
            n = int(num) if num.isdigit() else 50

            logs = read_last_logs(n)
            print("\n=== Log Output ===")
            print("\n".join(logs))
        else:
            print("Invalid selection. Please try again.")


# ---------------- Helper Input Function -------------------
def ask_filter_inputs():
    """Ask for filtering conditions in English."""
    country = input("Country (leave blank for no filter): ").strip() or None
    start_date = input("Start date YYYY-MM-DD (blank = no filter): ").strip() or None
    end_date = input("End date YYYY-MM-DD (blank = no filter): ").strip() or None
    age_group = (
        input(
            "Age group (0-17 / 18-49 / 50-64 / 65+ / Unknown, blank = no filter): "
        ).strip()
        or None
    )
    return country, start_date, end_date, age_group
