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
