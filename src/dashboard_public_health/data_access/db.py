"""Database connection"""

import os
from functools import lru_cache
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

load_dotenv()
# Load environment variables from .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Construct the SQLAlchemy connection string
DB_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Create the SQLAlchemy engine
@lru_cache(maxsize=1)
def get_engine():
    """Create and cache a SQLAlchemy engine for PostgreSQL."""
    engine = create_engine(DB_URL, echo=True, future=True, poolclass=NullPool)
    return engine


def write_df_to_db(df: pd.DataFrame, table_name: str, if_exists: str = "replace"):
    """Save a DataFrame into the PostgreSQL database as a table."""
    engine = get_engine()
    df.to_sql(table_name, con=engine, if_exists=if_exists, index=False)


def read_table(table_name: str) -> pd.DataFrame:
    """Read a table from PostgreSQL into a DataFrame."""
    engine = get_engine()
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)
