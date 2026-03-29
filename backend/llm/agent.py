"""
Tool-calling agent loop.

The agent is responsible for:
    1. Loading conversation history from the DB.
    2. Sending messages + available tool definitions to the LLM.
    3. Detecting tool calls in the LLM response and dispatching them
       to the appropriate functions in backend/tools/.
    4. Feeding tool results back into the conversation and looping
       until the LLM produces a plain text reply.
    5. Persisting the final assistant message to the DB.
"""

import json

from backend.llm.client import VLLMClient

# ---------------------------------------------------------------------------
# Application agent — tool dispatch map
# ---------------------------------------------------------------------------

def _build_tool_registry() -> dict:
    from backend.tools.experience import (
        save_experience,
        get_experience_details,
        update_experience_tool,
        update_experience_overview,
        search_experience,
    )
    from backend.tools.documents import (
        export_pdf,
        generate_cover_letter,
        generate_resume,
    )
    from backend.tools.research import research_url

    return {
        "save_experience": save_experience,
        "get_experience_details": get_experience_details,
        "update_experience_tool": update_experience_tool,
        "update_experience_overview": update_experience_overview,
        "search_experience": search_experience,
        "generate_resume": generate_resume,
        "generate_cover_letter": generate_cover_letter,
        "export_pdf": export_pdf,
        "research_url": research_url,
    }


def run_agent(username: str, application_id: str, user_message: str) -> str:
    """
    Main tool-calling agent loop for a single user turn.

    Steps:
        1. Load chat history for the application from the DB.
        2. Append the new user message.
        3. Call VLLMClient.chat() with all available tool definitions.
        4. If the response contains tool_calls, dispatch each to the
           registered tool function in backend/tools/.
        5. Append each tool result as a 'tool' role message and loop.
        6. When the LLM returns a plain text response (no tool calls),
           persist the assistant message to the DB and return it.

    Args:
        username: The authenticated user making the request.
        application_id: UUID of the active application context.
        user_message: The raw text input from the user.

    Returns:
        The assistant's final text response string.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Experience agent
# ---------------------------------------------------------------------------

EXPERIENCE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "upsert_experience",
            "description": (
                "Save an experience entry. Automatically creates a new entry or updates "
                "an existing one — you do not need to decide which. "
                "Call this once you have gathered all required information."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": (
                            "Complete description of the experience including ALL details "
                            "mentioned across the entire conversation: role, company/project "
                            "name, start and end dates, and key contributions."
                        ),
                    },
                },
                "required": ["description"],
            },
        },
    },
]

_EXPERIENCE_AGENT_SYSTEM = """\
You are a career assistant helping the user build their experience library. \
Your job is to collect information, not to elaborate on it.

STRICT RULES:
- NEVER invent, infer, or add details the user did not explicitly state.
- NEVER write bullet points summarising what you think the user did.
- Reflect information back using only the user's exact words.
- Ask one short, focused question at a time.

WHEN TO CALL upsert_experience:
- Only call upsert_experience once you have ALL FOUR: \
  (1) role/title, (2) company or project name, \
  (3) rough start and end dates, (4) at least one contribution or responsibility.
- Pass a COMPLETE description containing ALL details the user has mentioned \
  across the entire conversation — not just the latest message.
- The tool automatically handles whether to create or update. \
  You do not need to decide.

After the tool returns, tell the user only what title was saved, \
then ask what to add next.

## {username}'s saved experience

{experience_list}\
"""


def _build_experience_tool_registry() -> dict:
    from backend.tools.experience import upsert_experience
    return {"upsert_experience": upsert_experience}


def _render_experience_list(entries: list[dict]) -> str:
    if not entries:
        return "(none yet)"
    rows = ["| ID | Type | Title | Period |", "|----|------|-------|--------|"]
    for e in entries:
        start = e.get("start_date") or "?"
        end = e.get("end_date") or "present"
        rows.append(f"| {e['id']} | {e['type']} | {e['title']} | {start} – {end} |")
    return "\n".join(rows)


def run_experience_agent(
    username: str,
    user_message: str,
    history: list[dict],
) -> str:
    """
    Stateless tool-calling agent loop for the experience chat.

    History is passed in from the frontend (list of {role, content} dicts).
    No DB reads/writes for chat history — the experience entries themselves
    are the persistent artifact.

    Args:
        username: The authenticated user's username.
        user_message: The raw text input from the user.
        history: Prior conversation turns as [{role, content}, ...].

    Returns:
        The assistant's final text response string.
    """
    import backend.db.crud.experience as crud_experience

    entries = crud_experience.get_experience_for_user(username)
    experience_list = _render_experience_list(entries)
    system_prompt = _EXPERIENCE_AGENT_SYSTEM.format(
        username=username,
        experience_list=experience_list,
    )

    messages = (
        [{"role": "system", "content": system_prompt}]
        + history
        + [{"role": "user", "content": user_message}]
    )

    registry = _build_experience_tool_registry()

    for _ in range(10):
        response = VLLMClient().chat(messages, tools=EXPERIENCE_TOOLS)
        choice = response["choices"][0]
        assistant_msg = choice["message"]
        tool_calls = assistant_msg.get("tool_calls")
        print(f"[agent] finish_reason={choice.get('finish_reason')!r} tool_calls={bool(tool_calls)} content={assistant_msg.get('content', '')[:120]!r}")

        if tool_calls:
            messages.append(assistant_msg)

            for tool_call in tool_calls:
                name = tool_call["function"]["name"]
                raw_args = tool_call["function"]["arguments"]
                args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                args["username"] = username  # always inject — never trust the model

                try:
                    result = registry[name](**args)
                    print(f"[agent] tool {name} succeeded: {result}")
                except Exception as exc:
                    import traceback; traceback.print_exc()
                    result = {"error": str(exc)}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result, default=str),
                })
        else:
            return assistant_msg["content"]

    return (
        "I've reached my processing limit for this turn. "
        "Could you rephrase or break your request into smaller parts?"
    )
