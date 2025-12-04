# from dashboard_public_health.data_access.loader import load_csv_to_df
# from dashboard_public_health.data_access.db import write_df_to_db
# from dashboard_public_health.data_cleaning.clean import clean_data


# def main():
#     csv_path = "data/raw/public_health_surveillance_dataset.csv"  # 改成你真实的文件名
#     df = load_csv_to_df(csv_path)
#     print(f"Loaded Successful! {len(df)} rows from {csv_path}")

#     clean_data(df)
#     # table_name = "public_health_raw"
#     # write_df_to_db(df, table_name)
#     # print(f"Saved to table '{table_name}' in PostgreSQL")


# if __name__ == "__main__":
#     main()

# main.py
# src/public_health_insights/__main__.py
from .ui.cli import run_cli


def main():
    run_cli()


if __name__ == "__main__":
    main()
