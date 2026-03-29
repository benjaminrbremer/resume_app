# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend

```bash
# Initialize the database and file_db/ directory (run once, safe to re-run)
python3 -m backend.init_db

# Start the API server
uvicorn backend.main:app --reload

# Install dependencies
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install       # requires Node 18+
npm run dev       # starts on http://localhost:3000
npm run build
npm run lint
```

## Architecture

This is a monorepo with a Python/FastAPI backend and a Next.js 14 frontend. They are entirely separate — the frontend calls the backend over HTTP.

### Two databases

The app maintains two parallel stores for every user, and both must be kept in sync:

1. **SQLite** (`backend/resume_app.db`) — structured metadata. Schema is in `backend/db/models.py`. All connections go through `backend/db/connection.py`, which sets `row_factory = sqlite3.Row` and `PRAGMA foreign_keys = ON`.

2. **File DB** (`file_db/`) — markdown files for unstructured content. All path construction lives in `backend/file_db/operations.py` — no other file should build these paths directly. Layout:
   ```
   file_db/{username}/
       user_info.md
       experience/{uuid}.md        ← experience, jobs, AND skills share this dir
       applications/{app_id}/
           resume.md / resume.pdf
           cover_letter.md / cover_letter.pdf
           company_research.md
           job_info.md
           relevant_experience.md
       example_documents/
   ```

### UUID sharing across experience/jobs/skills

`experience`, `jobs`, and `skills` records all use UUID primary keys that are **globally unique across all three tables**. This is enforced by convention (all three generate with `uuid.uuid4()`) because their markdown files share a single `experience/` directory — the filename is the ID, so collisions would overwrite files. Never use sequential IDs for these tables.

### Side effects on record creation

Two CRUD functions trigger file DB operations as a side effect:
- `crud/users.py:create_user` → calls `file_db/operations.init_user_directories(username)`
- `crud/applications.py:create_application` → calls `file_db/operations.init_application_directory(username, app_id)`, which seeds 5 empty `.md` files

### Request flow

```
Frontend (Next.js) → Routers (FastAPI) → LLM Agent (llm/agent.py) → Tools (tools/) → DB + File DB
```

The routers are not a thin wrapper over CRUD — conversational requests go through `llm/agent.py`, which runs a tool-calling loop: send messages + tool definitions to vLLM, dispatch any tool calls to `tools/`, feed results back, repeat until a plain text response. Non-conversational routes (list/get) call CRUD directly.

### What's stubbed

The following raise `NotImplementedError` and need implementation:
- All routers (`backend/routers/*.py`) — return HTTP 501
- All tool functions (`backend/tools/*.py`)
- `VLLMClient.chat()` (`backend/llm/client.py`)
- `run_agent()` (`backend/llm/agent.py`)

Pydantic request/response schemas for all routes are already defined in `backend/routers/schemas.py`.

### Auth

Currently plain-text password comparison in `crud/users.py:verify_password`. No sessions or tokens — username is passed in query params/body for now. CORS middleware is in `backend/main.py` as a commented block; uncomment it when wiring the frontend.

### Frontend

Next.js 14 App Router in `frontend/app/`. Pages are placeholder-only. The two-column layout on `/applications/[id]` (document preview + chat) is the primary UI pattern for the application chat interface.

### Environment

Copy `.env.example` to `.env` and set:
- `DATABASE_URL` — path to SQLite file (relative to project root)
- `FILE_DB_ROOT` — path to file DB root (relative to project root)
- `VLLM_BASE_URL` — vLLM server base URL (OpenAI-compatible)
- `VLLM_MODEL_NAME` — model identifier
