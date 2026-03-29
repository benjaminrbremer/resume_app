import sqlite3
from contextlib import contextmanager

from backend.config import DATABASE_PATH


@contextmanager
def get_db_connection():
    """
    Context manager for SQLite connections.

    - Sets row_factory so rows are accessible by column name.
    - Enables foreign key enforcement on every connection.
    - Commits on clean exit; rolls back on any exception.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
