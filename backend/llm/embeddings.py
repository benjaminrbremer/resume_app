"""
Helpers for generating LLM summaries and embedding vectors for experience entries.
Used as a write-path side effect when experience/skill/job records are saved.
"""

import json
import logging

from backend.llm.client import VLLMClient

logger = logging.getLogger(__name__)


def _extract_text(response: dict) -> str:
    return response["choices"][0]["message"]["content"].strip()


def generate_summary_and_embedding(label: str, content: str) -> tuple[str, str]:
    """
    Generate a 1-2 sentence summary and an embedding vector for an experience entry.

    Args:
        label: A short descriptor, e.g. "job: Senior Engineer at Acme" or "skill: Python".
        content: The full markdown content of the experience file.

    Returns:
        A tuple of (summary_text, embedding_json_str).

    Raises:
        Exception: Propagated from VLLMClient on HTTP or parse errors.
    """
    client = VLLMClient()

    summary_input = f"{label}\n\n{content}".strip()
    summary_prompt = (
        "Summarize the following resume experience entry in 1-2 sentences. "
        "Be specific and use keywords relevant to job searching. "
        "Output only the summary, nothing else.\n\n"
        f"{summary_input}"
    )
    summary_response = client.chat(
        [{"role": "user", "content": summary_prompt}],
        tools=None,
    )
    summary = _extract_text(summary_response)

    embedding = client.embed(summary)
    return summary, json.dumps(embedding)


def try_generate_summary_and_embedding(label: str, content: str) -> tuple[str | None, str | None]:
    """
    Same as generate_summary_and_embedding but swallows exceptions so a
    failed embedding never blocks a save operation.
    """
    try:
        return generate_summary_and_embedding(label, content)
    except Exception as exc:
        logger.warning("Failed to generate summary/embedding for %r: %s", label, exc)
        return None, None
