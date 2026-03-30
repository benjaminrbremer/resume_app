import uuid

from backend.db.connection import get_db_connection


def create_example_document(
    username: str, original_filename: str, content_type: str | None = None
) -> dict:
    doc_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO example_documents (id, username, original_filename, content_type) VALUES (?, ?, ?, ?)",
            (doc_id, username, original_filename, content_type),
        )
    return get_example_document(doc_id)


def get_example_document(doc_id: str) -> dict | None:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM example_documents WHERE id = ?", (doc_id,)
        ).fetchone()
    return dict(row) if row else None


def get_example_documents_for_user(username: str) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM example_documents WHERE username = ? ORDER BY created_dt DESC",
            (username,),
        ).fetchall()
    return [dict(r) for r in rows]


def update_example_document(doc_id: str, **fields) -> dict | None:
    allowed = {"document_type"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return get_example_document(doc_id)
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [doc_id]
    with get_db_connection() as conn:
        conn.execute(f"UPDATE example_documents SET {set_clause} WHERE id = ?", values)
    return get_example_document(doc_id)


def delete_example_document(doc_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM example_documents WHERE id = ?", (doc_id,))
    return cursor.rowcount > 0
