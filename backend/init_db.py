"""
Database initialization script.

Run from the project root:
    python -m backend.init_db

Creates all SQLite tables (if they don't already exist) and ensures
the file_db/ root directory exists. Safe to re-run.
"""

import sys
from pathlib import Path

from backend.config import DATABASE_PATH, FILE_DB_PATH
from backend.db.connection import get_db_connection
from backend.db.models import ALL_TABLES


def init_db() -> None:
    # Ensure the directory for the SQLite file exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Initializing database at: {DATABASE_PATH}")
    with get_db_connection() as conn:
        for ddl in ALL_TABLES:
            table_name = ddl.strip().split()[5]  # "CREATE TABLE IF NOT EXISTS <name>"
            conn.execute(ddl)
            print(f"  OK  {table_name}")

    # Migrations: add columns that may not exist in older DBs
    _migrations = [
        ("example_documents", "document_type",
         "ALTER TABLE example_documents ADD COLUMN document_type TEXT "
         "CHECK(document_type IN ('resume', 'cover_letter', 'other'))"),
        ("experience", "summary",   "ALTER TABLE experience ADD COLUMN summary TEXT"),
        ("experience", "embedding", "ALTER TABLE experience ADD COLUMN embedding TEXT"),
        ("skills",     "summary",   "ALTER TABLE skills ADD COLUMN summary TEXT"),
        ("skills",     "embedding", "ALTER TABLE skills ADD COLUMN embedding TEXT"),
        ("jobs",       "summary",   "ALTER TABLE jobs ADD COLUMN summary TEXT"),
        ("jobs",       "embedding", "ALTER TABLE jobs ADD COLUMN embedding TEXT"),
        ("applications", "website_url", "ALTER TABLE applications ADD COLUMN website_url TEXT"),
    ]
    with get_db_connection() as conn:
        for table, col, ddl in _migrations:
            existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
            if col not in existing:
                conn.execute(ddl)
                print(f"  MIG {table}.{col}")

    print(f"\nInitializing file DB root at: {FILE_DB_PATH}")
    FILE_DB_PATH.mkdir(parents=True, exist_ok=True)
    print("  OK  file_db/")

    print("\nDone.")


if __name__ == "__main__":
    init_db()
