# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Patterns used throughout the backend

### Connection-per-operation
Each CRUD call opens and closes its own connection via `get_db_connection()`. There is no connection pooling or shared connection state.

### Update kwargs whitelisting
Every `update_*()` function accepts `**fields` and filters with a local `allowed` set. If no recognized fields are passed, it returns the current record without hitting the DB. New fields added to a table must be added to both the DDL in `db/models.py` and the `allowed` set in the corresponding CRUD function.

```python
allowed = {"title", "company", "start_date"}
updates = {k: v for k, v in fields.items() if k in allowed}
if not updates:
    return get_entity(id)
```

### Fresh fetch after write
Create and update functions return a fresh `SELECT` after the write, not the input values. This ensures the returned dict reflects DB defaults (e.g., `datetime('now')` columns).

### Return types
- Single record: `dict | None`
- List: `list[dict]`
- Delete: `bool` (True if a row was deleted)
- File reads: `str` (empty string if file missing — never raises)

### Running the server
```bash
uvicorn backend.main:app --reload
```
Run from the project root so relative paths in `config.py` resolve correctly.
