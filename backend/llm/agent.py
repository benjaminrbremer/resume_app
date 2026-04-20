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
import logging

from backend.llm.client import VLLMClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application agent — tool dispatch map
# ---------------------------------------------------------------------------

def _build_tool_registry() -> dict:
    from backend.tools.experience import search_experience
    from backend.tools.documents import (
        export_pdf,
        generate_cover_letter,
        generate_resume,
    )
    from backend.tools.research import research_url

    return {
        "search_experience": search_experience,
        "generate_resume": generate_resume,
        "generate_cover_letter": generate_cover_letter,
        "export_pdf": export_pdf,
        "research_url": research_url,
    }


_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "research_url",
            "description": "Fetch and summarize the content at a given URL (company website, job posting, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to fetch and summarize."}
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_experience",
            "description": "Select the user's most relevant experience entries for the current job application using vector search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "UUID of the target application."}
                },
                "required": ["application_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_resume",
            "description": "Generate a tailored resume in markdown for the current application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "UUID of the target application."}
                },
                "required": ["application_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_cover_letter",
            "description": "Generate a tailored cover letter in markdown for the current application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "UUID of the target application."}
                },
                "required": ["application_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "export_pdf",
            "description": "Convert a generated markdown document to PDF.",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "UUID of the target application."},
                    "document": {
                        "type": "string",
                        "enum": ["resume", "cover_letter"],
                        "description": "Which document to export.",
                    },
                },
                "required": ["application_id", "document"],
            },
        },
    },
]


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
    from backend.db.crud.applications import add_chat_message, get_chat_messages

    registry = _build_tool_registry()
    client = VLLMClient()

    history = get_chat_messages(application_id)
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]
    messages.append({"role": "user", "content": user_message})

    max_iterations = 10
    for _ in range(max_iterations):
        response = client.chat(messages, tools=_TOOL_DEFINITIONS)
        assistant_msg = response["choices"][0]["message"]

        # Per LMStudio gotcha: check tool_calls key directly, not finish_reason
        tool_calls = assistant_msg.get("tool_calls")
        if not tool_calls:
            final_content = assistant_msg.get("content", "").strip()
            add_chat_message(application_id, "user", user_message)
            add_chat_message(application_id, "assistant", final_content)
            return final_content

        messages.append(assistant_msg)

        for call in tool_calls:
            tool_name = call["function"]["name"]
            try:
                args = json.loads(call["function"].get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}

            # Always inject username — never trust the LLM to supply it correctly
            args["username"] = username

            fn = registry.get(tool_name)
            if fn is None:
                result = f"Unknown tool: {tool_name}"
                logger.warning("LLM called unknown tool: %s", tool_name)
            else:
                try:
                    result = fn(**args)
                    if result is None:
                        result = f"{tool_name} completed successfully."
                except Exception as exc:
                    result = f"Tool error: {exc}"
                    logger.error("Tool %s raised: %s", tool_name, exc)

            messages.append({
                "role": "tool",
                "tool_call_id": call.get("id", tool_name),
                "content": str(result),
            })

    last_content = "Agent loop exceeded maximum iterations without a final response."
    add_chat_message(application_id, "user", user_message)
    add_chat_message(application_id, "assistant", last_content)
    return last_content
