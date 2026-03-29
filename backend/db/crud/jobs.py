import uuid

from backend.db.connection import get_db_connection


def create_job(
    username: str,
    title: str,
    company: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    job_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO jobs (id, username, title, company, start_date, end_date) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (job_id, username, title, company, start_date, end_date),
        )
    return get_job(job_id)


def get_job(job_id: str) -> dict | None:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()
    return dict(row) if row else None


def get_jobs_for_user(username: str) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs WHERE username = ? ORDER BY start_date DESC",
            (username,),
        ).fetchall()
    return [dict(r) for r in rows]


def update_job(job_id: str, **fields) -> dict | None:
    allowed = {"title", "company", "start_date", "end_date"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return get_job(job_id)

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [job_id]

    with get_db_connection() as conn:
        conn.execute(f"UPDATE jobs SET {set_clause} WHERE id = ?", values)
    return get_job(job_id)


def delete_job(job_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# job_experience junction
# ---------------------------------------------------------------------------

def link_experience_to_job(job_id: str, experience_id: str) -> None:
    with get_db_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO job_experience (job_id, experience_id) VALUES (?, ?)",
            (job_id, experience_id),
        )


def unlink_experience_from_job(job_id: str, experience_id: str) -> None:
    with get_db_connection() as conn:
        conn.execute(
            "DELETE FROM job_experience WHERE job_id = ? AND experience_id = ?",
            (job_id, experience_id),
        )


def get_experience_for_job(job_id: str) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT e.* FROM experience e
            JOIN job_experience je ON e.id = je.experience_id
            WHERE je.job_id = ?
            ORDER BY e.start_date DESC
            """,
            (job_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# job_skills junction
# ---------------------------------------------------------------------------

def link_skill_to_job(job_id: str, skill_id: str) -> None:
    with get_db_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO job_skills (job_id, skill_id) VALUES (?, ?)",
            (job_id, skill_id),
        )


def unlink_skill_from_job(job_id: str, skill_id: str) -> None:
    with get_db_connection() as conn:
        conn.execute(
            "DELETE FROM job_skills WHERE job_id = ? AND skill_id = ?",
            (job_id, skill_id),
        )


def get_skills_for_job(job_id: str) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.* FROM skills s
            JOIN job_skills js ON s.id = js.skill_id
            WHERE js.job_id = ?
            ORDER BY s.name
            """,
            (job_id,),
        ).fetchall()
    return [dict(r) for r in rows]
