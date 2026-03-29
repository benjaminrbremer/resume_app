# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Role of tools

These functions are called by the LLM agent in `llm/agent.py`, not by the routers directly. The agent dispatches them by name — the name in the tool registry must match the function name exactly.

To make a new tool callable by the LLM, add it here and register it in `llm/agent.py:_build_tool_registry()`.

## Implementing a tool

Each stub's docstring is its specification. When implementing:
1. Import from `file_db/operations.py` for all file reads/writes — never build paths directly.
2. Import from `db/crud/` for any DB lookups needed.
3. For tools that are themselves LLM calls (`search_experience`, `generate_resume`, `generate_cover_letter`), use `llm/client.VLLMClient`.

## File I/O contract

| Tool | Reads | Writes |
|---|---|---|
| `persist_experience` | — | `experience/{id}.md` |
| `update_experience_overview` | — | `user_info.md` |
| `search_experience` | `experience/*.md`, `job_info.md`, `company_research.md` | `relevant_experience.md` |
| `generate_resume` | `user_info.md`, `relevant_experience.md`, `job_info.md`, `example_documents/` | `resume.md` |
| `generate_cover_letter` | `resume.md`, `job_info.md`, `company_research.md`, `example_documents/` | `cover_letter.md` |
| `export_pdf` | `resume.md` or `cover_letter.md` | `resume.pdf` or `cover_letter.pdf` |
| `research_url` | external URL | (returns string, caller writes) |

## Scaling note

`search_experience` loads all experience files for a user into context. This will hit LLM context window limits for users with many entries. Document any chunking strategy here when implemented.
