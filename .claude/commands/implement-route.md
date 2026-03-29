Implement the FastAPI route described below.

Route to implement: $ARGUMENTS

Steps:
1. Read the relevant router file in `backend/routers/` to find the stub endpoint.
2. Read `backend/routers/schemas.py` to understand the request/response models.
3. Determine whether this is a CRUD route (call `db/crud/` directly) or a conversational route (call `llm/agent.run_agent()`). See `backend/routers/CLAUDE.md` for the distinction.
4. Implement the route body, replacing the 501 stub. Return appropriate HTTP status codes (200 for success, 404 if a record isn't found, 400 for validation errors).
5. If the route needs a response schema not yet in `schemas.py`, add it there.

Do not change the route's URL, method, or function signature.
