from datetime import datetime, timezone

from backend.db.connection import get_db_connection
from backend.file_db.operations import init_user_directories


def create_user(username: str, password: str, **profile_fields) -> dict:
    """
    Insert a new user record and initialize their file DB directories.
    Raises sqlite3.IntegrityError if username already exists.
    """
    allowed = {
        "firstname", "lastname", "linkedin_url", "profile_url",
        "github_url", "email", "phone", "objective",
    }
    fields = {k: v for k, v in profile_fields.items() if k in allowed}
    columns = ["username", "password"] + list(fields.keys())
    placeholders = ", ".join("?" for _ in columns)
    values = [username, password] + list(fields.values())

    with get_db_connection() as conn:
        conn.execute(
            f"INSERT INTO users ({', '.join(columns)}) VALUES ({placeholders})",
            values,
        )

    init_user_directories(username)
    return get_user_by_username(username)


def get_user_by_username(username: str) -> dict | None:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return dict(row) if row else None


def update_user(username: str, **fields) -> dict | None:
    allowed = {
        "firstname", "lastname", "linkedin_url", "profile_url",
        "github_url", "email", "phone", "objective", "password",
    }
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return get_user_by_username(username)

    updates["last_update_dt"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [username]

    with get_db_connection() as conn:
        conn.execute(
            f"UPDATE users SET {set_clause} WHERE username = ?", values
        )
    return get_user_by_username(username)


def delete_user(username: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM users WHERE username = ?", (username,)
        )
    return cursor.rowcount > 0


def verify_password(username: str, password: str) -> bool:
    """
    Check username/password against the DB.
    Plain string comparison — intentionally simple for development.
    Replace with bcrypt check when hardening for production.
    """
    user = get_user_by_username(username)
    if user is None:
        return False
    return user["password"] == password
