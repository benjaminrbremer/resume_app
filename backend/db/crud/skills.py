import uuid

from backend.db.connection import get_db_connection


def create_skill(username: str, name: str, proficiency: str | None = None) -> dict:
    skill_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO skills (id, username, name, proficiency) VALUES (?, ?, ?, ?)",
            (skill_id, username, name, proficiency),
        )
    return get_skill(skill_id)


def get_skill(skill_id: str) -> dict | None:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM skills WHERE id = ?", (skill_id,)
        ).fetchone()
    return dict(row) if row else None


def get_skills_for_user(username: str) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM skills WHERE username = ? ORDER BY name", (username,)
        ).fetchall()
    return [dict(r) for r in rows]


def update_skill(skill_id: str, **fields) -> dict | None:
    allowed = {"name", "proficiency"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return get_skill(skill_id)

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [skill_id]

    with get_db_connection() as conn:
        conn.execute(f"UPDATE skills SET {set_clause} WHERE id = ?", values)
    return get_skill(skill_id)


def delete_skill(skill_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
    return cursor.rowcount > 0
