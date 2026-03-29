# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Hard rule: no path construction outside this module

All `file_db/` path logic lives in `operations.py`. No other file should construct paths into `file_db/` directly. Add a new internal `_helper()` function here if a new path is needed.

## Seeded files

Every new application directory is initialized with exactly these 5 empty files:
```
resume.md, cover_letter.md, company_research.md, job_info.md, relevant_experience.md
```
This means `read_application_file()` will always return `""` rather than raising on a fresh application — callers should treat `""` as "not yet generated".

## read_* return convention

All `read_*` functions return `""` (empty string) if the file doesn't exist. They never raise `FileNotFoundError`. This is intentional so tool functions can safely read before writing without defensive checks.

## Adding a new application file

If a new file type is needed per application (e.g., `interview_notes.md`):
1. Add its filename to `_APPLICATION_SEED_FILES` in `operations.py`.
2. Add dedicated `read_*/write_*` helpers or use `read_application_file(username, app_id, "interview_notes.md")` directly.
