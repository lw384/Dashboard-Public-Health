# application/ingestion_service.py
from infrastructure.csv_reader import read_csv
from domain.rules import from_row
from infrastructure.csv_reader import read_csv
from infrastructure.sqlite_repository import init_db, save_records
from domain.rules import from_row


def load_dataset_from_csv(path: str):
    df = read_csv(path)
    records = [from_row(row) for _, row in df.iterrows()]
    return records


def load_and_persist_from_csv(path: str) -> int:
    init_db()
    df = read_csv(path)
    records = [from_row(row) for _, row in df.iterrows()]
    save_records(records)
    return len(records)
