import uuid

from backend.db.connection import get_db_connection
from backend.file_db.operations import init_application_directory

VALID_ROLES = ("user", "assistant", "tool")


def create_application(username: str, title: str, company: str) -> dict:
    """
    Insert a new application record and initialize its file DB directory
    (seeding all required markdown files as empty).
    """
    app_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO applications (id, username, title, company) VALUES (?, ?, ?, ?)",
            (app_id, username, title, company),
        )
    init_application_directory(username, app_id)
    return get_application(app_id)


def get_application(app_id: str) -> dict | None:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
    return dict(row) if row else None


def get_applications_for_user(username: str) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM applications WHERE username = ? ORDER BY started_dt DESC",
            (username,),
        ).fetchall()
    return [dict(r) for r in rows]


def update_application(app_id: str, **fields) -> dict | None:
    allowed = {"title", "company", "outcome", "submitted_dt", "outcome_dt"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return get_application(app_id)

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [app_id]

    with get_db_connection() as conn:
        conn.execute(f"UPDATE applications SET {set_clause} WHERE id = ?", values)
    return get_application(app_id)


# ---------------------------------------------------------------------------
# Chat messages
# ---------------------------------------------------------------------------

def add_chat_message(application_id: str, role: str, content: str) -> dict:
    if role not in VALID_ROLES:
        raise ValueError(f"role must be one of {VALID_ROLES}")
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO chat_messages (application_id, role, content) VALUES (?, ?, ?)",
            (application_id, role, content),
        )
        msg_id = cursor.lastrowid

    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM chat_messages WHERE id = ?", (msg_id,)
        ).fetchone()
    return dict(row)


def get_chat_messages(application_id: str) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM chat_messages WHERE application_id = ? ORDER BY created_dt ASC",
            (application_id,),
        ).fetchall()
    return [dict(r) for r in rows]
