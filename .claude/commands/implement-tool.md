Implement the LLM tool function described below.

Tool to implement: $ARGUMENTS

Steps:
1. Read the stub in `backend/tools/` — the docstring is the specification.
2. Read `backend/tools/CLAUDE.md` for the file I/O contract table (what files each tool reads and writes).
3. Use `backend/file_db/operations.py` for all file reads/writes — never construct file paths directly.
4. Use `backend/db/crud/` for any DB lookups needed.
5. If this tool is itself an LLM call (e.g., `search_experience`, `generate_resume`, `generate_cover_letter`), use `llm/client.VLLMClient` to call the vLLM server.
6. Replace `raise NotImplementedError` with the implementation. Keep the function signature unchanged.

After implementing, verify the tool name in `backend/llm/agent.py:_build_tool_registry()` matches the function name exactly.
