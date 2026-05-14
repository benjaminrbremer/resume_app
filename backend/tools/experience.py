"""
Tools for selecting relevant experience entries for a job application.
"""

import logging

from backend.db.crud.experience import get_experience_for_user
from backend.db.crud.jobs import get_jobs_for_user
from backend.db.crud.skills import get_skills_for_user
from backend.file_db.operations import read_application_file, read_experience_file, write_application_file
from backend.llm.client import VLLMClient
from backend.utils import cosine_similarity, parse_embedding

logger = logging.getLogger(__name__)

_TOP_N = 10
_MIN_SCORE = 0.25


def _get_embedding_for_record(record: dict, username: str) -> list[float] | None:
    """Return a cached embedding or generate one on the fly for legacy records."""
    cached = parse_embedding(record.get("embedding"))
    if cached:
        return cached

    item_id = record["id"]
    content = read_experience_file(username, item_id)
    if record.get("type"):
        label = f"{record['type']}: {record['title']}"
    elif record.get("company"):
        label = f"job: {record['title']} at {record['company']}"
    else:
        label = f"skill: {record.get('name', record.get('title', ''))}"

    summary_input = f"{label}\n\n{content}".strip()
    if not summary_input.strip():
        return None

    try:
        return VLLMClient().embed(summary_input[:2000])
    except Exception as exc:
        logger.warning("Failed to embed record %s on the fly: %s", item_id, exc)
        return None


def search_experience(username: str, application_id: str) -> str:
    """
    Select and rank the user's most relevant experience entries for a job application
    using cosine similarity between embeddings.

    Reads job_info.md and company_research.md for query context, then ranks all
    experience, jobs, and skills by similarity. Writes the top results to
    relevant_experience.md under the application.

    Args:
        username: The authenticated user's username.
        application_id: UUID of the target application.

    Returns:
        The markdown content written to relevant_experience.md.
    """
    job_info = read_application_file(username, application_id, "job_info.md")
    company_research = read_application_file(username, application_id, "company_research.md")
    query_text = f"{job_info}\n\n{company_research}".strip()

    if not query_text:
        result = "# Relevant Experience\n\nNo job information available to search against."
        write_application_file(username, application_id, "relevant_experience.md", result)
        return result

    try:
        query_vec = VLLMClient().embed(query_text[:3000])
    except Exception as exc:
        logger.error("Failed to embed query for experience search: %s", exc)
        result = "# Relevant Experience\n\nFailed to generate query embedding."
        write_application_file(username, application_id, "relevant_experience.md", result)
        return result

    # Gather all candidates across experience, jobs, and skills
    candidates: list[dict] = []
    for record in get_experience_for_user(username):
        candidates.append({**record, "_label": f"{record['type']}: {record['title']}"})
    for record in get_jobs_for_user(username):
        candidates.append({**record, "_label": f"job: {record['title']} at {record['company']}"})
    for record in get_skills_for_user(username):
        candidates.append({**record, "_label": f"skill: {record.get('name', '')}"})

    scored: list[tuple[float, dict]] = []
    for record in candidates:
        vec = _get_embedding_for_record(record, username)
        if vec is None:
            continue
        score = cosine_similarity(query_vec, vec)
        if score >= _MIN_SCORE:
            scored.append((score, record))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:_TOP_N]

    lines = ["# Relevant Experience", "", "<!-- UUIDs selected for this application -->"]
    for score, record in top:
        lines.append(f"- {record['id']} | {record['_label']} | score: {score:.3f}")

    result = "\n".join(lines)
    write_application_file(username, application_id, "relevant_experience.md", result)
    return result
