from dashboard_public_health.data_access.loader import load_csv_to_df
from dashboard_public_health.data_access.db import write_df_to_db


def main():
    csv_path = "data/raw/public_health_surveillance_dataset.csv"  # 改成你真实的文件名
    df = load_csv_to_df(csv_path)
    print(f"Loaded Successful! {len(df)} rows from {csv_path}")

    table_name = "public_health_raw"
    write_df_to_db(df, table_name)
    print(f"Saved to table '{table_name}' in PostgreSQL")


if __name__ == "__main__":
    main()
