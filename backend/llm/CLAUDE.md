# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## VLLMClient

Expects an OpenAI-compatible `/v1/chat/completions` endpoint. The `tools` parameter maps to OpenAI's function-calling format. Use `httpx` (already in requirements) for the HTTP call — not `requests`.

## Tool registry

`_build_tool_registry()` in `agent.py` returns a `dict[str, Callable]` mapping tool names to functions. Imports are deferred inside the function to avoid circular imports at module load time. When adding a new tool:
1. Implement it in `tools/`.
2. Import and add it to the dict in `_build_tool_registry()`.

## Agent loop (when implementing `run_agent`)

Expected flow:
1. `crud/applications.get_chat_messages(application_id)` → load history
2. Append `{"role": "user", "content": user_message}`
3. `VLLMClient.chat(messages, tools=list(_build_tool_registry().values()))` — send to LLM
4. If response has `tool_calls`: dispatch each, append `{"role": "tool", ...}` results, go to step 3
5. On plain text response: `crud/applications.add_chat_message(application_id, "assistant", content)`, return content

## Context

`run_agent` receives `application_id` so it can scope chat history and file DB paths to the active application. `username` is needed to resolve file DB paths.
