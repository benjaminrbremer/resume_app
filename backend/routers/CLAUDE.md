# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stub pattern

All routes currently return HTTP 501. When implementing a route, replace the `JSONResponse(status_code=501, ...)` body with real logic. The route signature, schema imports, and URL structure should not change.

## Username sourcing

Until session auth is implemented, username is passed explicitly:
- `GET /` list routes — query parameter: `async def list_items(username: str)`
- `POST /` create routes — request body field in the schema (see `schemas.py`)
- `GET/PUT/DELETE /{id}` routes — not needed (ID is sufficient to look up the record)

## Schemas

All Pydantic models live in `schemas.py`. Create/Update pairs exist for each entity. Update schemas have all fields as `str | None = None` so partial updates are supported.

## Conversational vs. CRUD routes

- **CRUD routes** (`GET`, `PUT`, `DELETE /{id}`) will call `db/crud/` functions directly when implemented.
- **Conversational routes** (`/chat`, `/generate-resume`, `/generate-cover-letter`) will call `llm/agent.run_agent()` — not CRUD functions directly.

## Adding a new route

1. Add the Pydantic schema to `schemas.py`.
2. Add the stub endpoint to the appropriate router file.
3. Register the router in `main.py` if it's a new file.
