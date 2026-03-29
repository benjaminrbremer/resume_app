"""
LLM-callable tools for managing experience data.
"""

import json

import backend.db.crud.experience as crud_experience
from backend.file_db.operations import (
    read_experience_file,
    write_experience_file,
    write_user_info,
)
from backend.llm.client import VLLMClient

_EXTRACTION_SYSTEM = """\
You are a structured data extractor. Given a description of a professional experience, \
project, or skill set, extract the following fields and return ONLY valid JSON with \
exactly these keys:

{
  "type": "<one of: general | job_project | personal>",
  "title": "<concise title, e.g. 'Senior Software Engineer at Acme Corp'>",
  "start_date": "<YYYY-MM or null>",
  "end_date": "<YYYY-MM or null>",
  "summary": "<2-4 sentence markdown paragraph summarising the experience>"
}

Rules:
- type="general" for broad skills or general background
- type="job_project" for work at an employer or freelance contract
- type="personal" for personal projects, open-source, or volunteer work
- Dates must be YYYY-MM format or null if unknown or ongoing
- summary must be markdown-safe prose (no headings)
- Return ONLY the JSON object, no surrounding text or code fences\
"""


def _extract_experience_fields(description: str) -> dict:
    """
    Inner LLM call that parses a natural-language experience description into
    structured fields. Returns a dict with keys: type, title, start_date,
    end_date, summary.

    Retries once with a nudge if the first response is not valid JSON.
    Raises ValueError if both attempts fail.
    """
    client = VLLMClient()
    messages = [
        {"role": "system", "content": _EXTRACTION_SYSTEM},
        {"role": "user", "content": description},
    ]
    response = client.chat(messages)
    raw = response["choices"][0]["message"]["content"].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Retry with an explicit nudge
        messages.append({"role": "assistant", "content": raw})
        messages.append({
            "role": "user",
            "content": (
                "Your previous response was not valid JSON. "
                "Return ONLY the JSON object with no surrounding text or code fences."
            ),
        })
        retry_response = client.chat(messages)
        retry_raw = retry_response["choices"][0]["message"]["content"].strip()
        try:
            return json.loads(retry_raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Could not parse experience fields from LLM response: {retry_raw!r}"
            ) from exc


def _build_markdown(fields: dict, record: dict) -> str:
    start = fields.get("start_date") or "unknown"
    end = fields.get("end_date") or "present"
    return (
        f"# {record['title']}\n\n"
        f"**Type**: {record['type']}  \n"
        f"**Period**: {start} – {end}\n\n"
        f"{fields.get('summary', '')}\n"
    )


# Words stripped before matching titles — stop words, corporate suffixes, and
# generic job-title words so that distinctive company/project names are what remains.
_TITLE_NOISE_WORDS = {
    "at", "in", "the", "a", "an", "of", "for", "and", "or", "with", "by", "to",
    "inc", "llc", "ltd", "corp", "co", "company",
    "engineer", "engineering", "developer", "development", "manager", "management",
    "director", "senior", "junior", "intern", "internship", "associate", "lead",
    "staff", "principal", "software", "data", "product", "project", "research",
    "scientist", "analyst", "consultant", "specialist", "coordinator", "architect",
    "designer", "executive", "officer", "head", "chief", "vp", "vice", "president",
    "employee", "contractor", "freelance",
}


def _title_keywords(title: str) -> set[str]:
    """Return lowercase alphabetic words from a title after stripping noise words."""
    import re
    words = re.findall(r"[a-zA-Z]+", title.lower())
    return {w for w in words if w not in _TITLE_NOISE_WORDS and len(w) > 1}


def _find_matching_entry(new_title: str, existing: list[dict]) -> dict | None:
    """
    Return the first existing entry whose title shares at least one keyword with
    new_title, or None if no match is found.
    """
    new_kws = _title_keywords(new_title)
    if not new_kws:
        return None
    for entry in existing:
        if new_kws & _title_keywords(entry["title"]):
            return entry
    return None


def upsert_experience(username: str, description: str) -> dict:
    """
    Create or update an experience entry from a complete natural-language description.

    Extracts structured fields from the description, then checks whether an existing
    entry with a matching title already exists for this user. If one is found it is
    updated in-place; otherwise a new entry is created. This keeps the create-vs-update
    decision in code rather than leaving it to the LLM.

    Args:
        username: The authenticated user's username.
        description: Full description of the experience including ALL details gathered
                     across the conversation (role, company, dates, contributions).

    Returns:
        The created or updated experience record dict, with an "_action" key set to
        "created" or "updated".
    """
    fields = _extract_experience_fields(description)
    existing = crud_experience.get_experience_for_user(username)
    match = _find_matching_entry(fields["title"], existing)

    if match:
        record = crud_experience.update_experience(
            match["id"],
            type=fields["type"],
            title=fields["title"],
            start_date=fields.get("start_date"),
            end_date=fields.get("end_date"),
        )
        write_experience_file(username, match["id"], _build_markdown(fields, record))
        return {**record, "_action": "updated"}
    else:
        record = crud_experience.create_experience(
            username=username,
            type=fields["type"],
            title=fields["title"],
            start_date=fields.get("start_date"),
            end_date=fields.get("end_date"),
        )
        write_experience_file(username, record["id"], _build_markdown(fields, record))
        return {**record, "_action": "created"}


def save_experience(username: str, description: str) -> dict:
    """
    Create a new experience entry from a natural-language description.

    Makes an inner LLM call to extract structured fields and a markdown summary,
    creates the SQLite record, and writes the markdown file to the file DB.

    Args:
        username: The authenticated user's username.
        description: Full natural-language description of the experience.

    Returns:
        The newly created experience record dict.
    """
    fields = _extract_experience_fields(description)
    record = crud_experience.create_experience(
        username=username,
        type=fields["type"],
        title=fields["title"],
        start_date=fields.get("start_date"),
        end_date=fields.get("end_date"),
    )
    write_experience_file(username, record["id"], _build_markdown(fields, record))
    return record


def get_experience_details(username: str, exp_id: str) -> dict:
    """
    Fetch the full metadata and existing markdown summary for a saved experience entry.

    Call this before update_experience_tool when the user wants to amend an existing
    entry — use the returned content to construct a complete merged description.

    Args:
        username: The authenticated user's username.
        exp_id: UUID of the experience record.

    Returns:
        The experience record dict with an additional "markdown" key containing
        the current file content. Returns None for "markdown" if no file exists yet.
    """
    record = crud_experience.get_experience(exp_id)
    if record is None:
        raise ValueError(f"No experience record found for id={exp_id!r}")
    existing_markdown = read_experience_file(username, exp_id)
    return {**record, "markdown": existing_markdown}


def update_experience_tool(username: str, exp_id: str, description: str) -> dict:
    """
    Update an existing experience entry from a complete merged description.

    description should be the full combined content (original + amendments), not
    just the delta. Call get_experience_details first to retrieve existing content.

    Args:
        username: The authenticated user's username.
        exp_id: UUID of the experience record to update.
        description: Complete merged natural-language description.

    Returns:
        The updated experience record dict.
    """
    fields = _extract_experience_fields(description)
    record = crud_experience.update_experience(
        exp_id,
        type=fields["type"],
        title=fields["title"],
        start_date=fields.get("start_date"),
        end_date=fields.get("end_date"),
    )
    if record is None:
        raise ValueError(f"No experience record found for id={exp_id!r}")
    write_experience_file(username, exp_id, _build_markdown(fields, record))
    return record


def update_experience_overview(username: str, text_chunk: str) -> None:
    """
    Rewrite the user's profile overview (user_info.md) with the given text.

    Args:
        username: The user whose user_info.md to update.
        text_chunk: Updated profile overview text in markdown.
    """
    write_user_info(username, text_chunk)


def search_experience(username: str, application_id: str) -> None:
    """
    LLM call that identifies which of the user's experience entries are most
    relevant to a given job application and persists the results.

    Process:
        1. Loads all experience markdown files for the user from the file DB.
        2. Loads job_info.md and company_research.md for the application.
        3. Calls the LLM to rank/select the most relevant experience IDs.
        4. Writes the selected IDs to:
               file_db/{username}/applications/{application_id}/relevant_experience.md

    Known scaling concern: for users with many experience entries this will
    eventually approach context window limits. Future versions should chunk
    or embed experience entries.

    Args:
        username: The user whose experience library to search.
        application_id: UUID of the application being tailored.
    """
    raise NotImplementedError
