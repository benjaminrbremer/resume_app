import uuid

from backend.db.connection import get_db_connection

VALID_TYPES = ("general", "job", "project", "volunteer")


def create_experience(
    username: str,
    type: str,
    title: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    if type not in VALID_TYPES:
        raise ValueError(f"type must be one of {VALID_TYPES}")
    exp_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO experience (id, username, type, title, start_date, end_date) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (exp_id, username, type, title, start_date, end_date),
        )
    return get_experience(exp_id)


def get_experience(exp_id: str) -> dict | None:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM experience WHERE id = ?", (exp_id,)
        ).fetchone()
    return dict(row) if row else None


def get_experience_for_user(username: str) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM experience WHERE username = ? ORDER BY start_date DESC",
            (username,),
        ).fetchall()
    return [dict(r) for r in rows]


def update_experience(exp_id: str, **fields) -> dict | None:
    allowed = {"type", "title", "start_date", "end_date"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return get_experience(exp_id)

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [exp_id]

    with get_db_connection() as conn:
        conn.execute(f"UPDATE experience SET {set_clause} WHERE id = ?", values)
    return get_experience(exp_id)


def delete_experience(exp_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM experience WHERE id = ?", (exp_id,))
    return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# experience_skills junction
# ---------------------------------------------------------------------------

def link_skill_to_experience(experience_id: str, skill_id: str) -> None:
    with get_db_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO experience_skills (experience_id, skill_id) VALUES (?, ?)",
            (experience_id, skill_id),
        )


def unlink_skill_from_experience(experience_id: str, skill_id: str) -> None:
    with get_db_connection() as conn:
        conn.execute(
            "DELETE FROM experience_skills WHERE experience_id = ? AND skill_id = ?",
            (experience_id, skill_id),
        )


def get_skills_for_experience(experience_id: str) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.* FROM skills s
            JOIN experience_skills es ON s.id = es.skill_id
            WHERE es.experience_id = ?
            ORDER BY s.name
            """,
            (experience_id,),
        ).fetchall()
    return [dict(r) for r in rows]
