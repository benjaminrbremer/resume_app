# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ID strategy

- `users` and `chat_messages` use `INTEGER PRIMARY KEY AUTOINCREMENT`.
- `skills`, `experience`, `jobs`, `applications` use `TEXT` UUID primary keys generated with `uuid.uuid4()`.
- The UUID requirement for skills/experience/jobs exists because they share a single `file_db/{username}/experience/` directory — filenames are IDs, so collisions would silently overwrite files.

## Junction tables

`job_experience`, `experience_skills`, `job_skills` follow an identical pattern:

- **Link**: `INSERT OR IGNORE` — silently skips if the relationship already exists.
- **Unlink**: `DELETE` by composite key.
- **Fetch**: `JOIN` from the target table filtered by the source ID.

When adding a new many-to-many relationship, follow this pattern in the entity that "owns" the relationship (e.g., `jobs.py` owns `job_experience` and `job_skills`).

## Schema changes

1. Add or modify the DDL constant in `models.py`.
2. Update the `allowed` set in the corresponding `crud/*.py` update function.
3. Re-run `python3 -m backend.init_db` — `IF NOT EXISTS` means existing tables are unaffected. For column additions, you'll need to `ALTER TABLE` or drop and recreate in development.

## Datetime handling

Only `users` has auto-managed timestamps (`created_dt`, `last_update_dt`). Application lifecycle fields (`submitted_dt`, `outcome_dt`) are `NULL` by default and must be set explicitly via `update_application()`.
