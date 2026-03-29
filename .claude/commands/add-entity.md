Add a new data entity to the resume app following existing patterns.

Entity to add: $ARGUMENTS

Steps:
1. **DB schema** (`backend/db/models.py`): Add a `CREATE TABLE IF NOT EXISTS` DDL constant. Use `TEXT PRIMARY KEY` (UUID) unless this entity doesn't appear in the file DB. Add it to `ALL_TABLES` in dependency order.

2. **CRUD module** (`backend/db/crud/{entity}.py`): Follow the pattern in any existing CRUD file exactly:
   - `create_*` — generate UUID, INSERT, return fresh fetch
   - `get_*` — return `dict | None`
   - `get_*s_for_user` — return `list[dict]`, ORDER BY something sensible
   - `update_*` — kwargs whitelisting with `allowed = {set}`, return fresh fetch
   - `delete_*` — return `bool`
   - Junction helpers if there are many-to-many relationships: `link_*`, `unlink_*`, `get_*_for_*`

3. **File DB** (if needed, `backend/file_db/operations.py`): Add internal path helper and public read/write functions following the existing pattern.

4. **Schemas** (`backend/routers/schemas.py`): Add `{Entity}Create` and `{Entity}Update` Pydantic models.

5. **Router** (`backend/routers/{entity}.py`): Create a new router file with stubbed REST endpoints. Register it in `backend/main.py`.

6. **Re-initialize DB**: Run `python3 -m backend.init_db` — existing tables are unaffected.
