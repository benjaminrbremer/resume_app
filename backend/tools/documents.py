"""
Tools for generating and exporting resume/cover letter documents.
"""

import logging
from pathlib import Path

from backend.config import FILE_DB_PATH
from backend.db.crud.documents import get_example_documents_for_user
from backend.file_db.operations import read_application_file, read_experience_file, write_application_file
from backend.llm.client import VLLMClient
from backend.utils import parse_relevant_uuids

logger = logging.getLogger(__name__)


def _load_example_documents(username: str, doc_type: str) -> list[str]:
    """Load up to 2 example documents of the given type (resume or cover_letter)."""
    records = get_example_documents_for_user(username)
    contents = []
    for rec in records:
        if rec.get("document_type") != doc_type:
            continue
        doc_path = FILE_DB_PATH / username / "example_documents" / rec["id"]
        if not doc_path.exists():
            continue
        try:
            text = doc_path.read_text(encoding="utf-8", errors="replace")
            if text.strip():
                contents.append(text)
        except Exception:
            pass
        if len(contents) >= 2:
            break
    return contents


def generate_resume(username: str, application_id: str, changes_prompt: str | None = None) -> None:
    """
    Generate a tailored resume in markdown format for the given application.

    Uses the following inputs from the file DB:
        - file_db/{username}/applications/{application_id}/relevant_experience.md
        - file_db/{username}/applications/{application_id}/job_info.md
        - file_db/{username}/example_documents/ (for style/voice reference)

    Writes the result to:
        file_db/{username}/applications/{application_id}/resume.md
    """
    relevant_md = read_application_file(username, application_id, "relevant_experience.md")
    job_info = read_application_file(username, application_id, "job_info.md")

    uuids = parse_relevant_uuids(relevant_md)
    experience_sections = []
    for uid in uuids:
        content = read_experience_file(username, uid)
        if content.strip():
            experience_sections.append(content)

    example_docs = _load_example_documents(username, "resume")

    system_prompt = (
        "You are a professional resume writer. "
        "Create a tailored, polished resume in markdown format based on the provided information. "
        "Emphasize experience and skills most relevant to the target role. "
        "Use clear section headers (## Summary, ## Experience, ## Skills, etc.). "
    )
    if example_docs:
        system_prompt += "Follow the style, tone, and structure of the example resume(s) provided. "
    system_prompt += "Output only the resume markdown, nothing else."

    user_content_parts = [f"## Target Job\n{job_info}"]
    if example_docs:
        user_content_parts.append("## Example Resume(s)\n" + "\n\n---\n\n".join(example_docs))
    if experience_sections:
        user_content_parts.append("## Experience Entries\n" + "\n\n---\n\n".join(experience_sections))
    if changes_prompt:
        user_content_parts.append(f"## Requested Changes\n{changes_prompt}")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "\n\n".join(user_content_parts)},
    ]

    client = VLLMClient()
    response = client.chat(messages, tools=None)
    content = response["choices"][0]["message"]["content"].strip()
    write_application_file(username, application_id, "resume.md", content)


def generate_cover_letter(username: str, application_id: str, changes_prompt: str | None = None) -> None:
    """
    Generate a tailored cover letter in markdown format for the given application.

    Uses the following inputs from the file DB:
        - file_db/{username}/applications/{application_id}/resume.md
        - file_db/{username}/applications/{application_id}/job_info.md
        - file_db/{username}/applications/{application_id}/company_research.md
        - file_db/{username}/example_documents/ (for style/voice reference)

    Writes the result to:
        file_db/{username}/applications/{application_id}/cover_letter.md
    """
    resume = read_application_file(username, application_id, "resume.md")
    job_info = read_application_file(username, application_id, "job_info.md")
    company_research = read_application_file(username, application_id, "company_research.md")
    example_docs = _load_example_documents(username, "cover_letter")

    system_prompt = (
        "You are a professional cover letter writer. "
        "Write a compelling, concise cover letter in markdown format tailored to the target role. "
        "Reference specific details from the company research to show genuine interest. "
        "Draw from the resume to highlight the most relevant experience. "
    )
    if example_docs:
        system_prompt += "Follow the style and tone of the example cover letter(s) provided. "
    system_prompt += "Output only the cover letter markdown, nothing else."

    user_content_parts = [f"## Target Job\n{job_info}"]
    if company_research.strip():
        user_content_parts.append(f"## Company Research\n{company_research}")
    if resume.strip():
        user_content_parts.append(f"## Applicant Resume\n{resume}")
    if example_docs:
        user_content_parts.append("## Example Cover Letter(s)\n" + "\n\n---\n\n".join(example_docs))
    if changes_prompt:
        user_content_parts.append(f"## Requested Changes\n{changes_prompt}")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "\n\n".join(user_content_parts)},
    ]

    client = VLLMClient()
    response = client.chat(messages, tools=None)
    content = response["choices"][0]["message"]["content"].strip()
    write_application_file(username, application_id, "cover_letter.md", content)


def export_pdf(username: str, application_id: str, document: str) -> None:
    """
    Convert a markdown document to PDF and save it alongside the source file.

    Args:
        username: The authenticated user.
        application_id: UUID of the application.
        document: Which document to export. Must be 'resume' or 'cover_letter'.

    Output paths:
        resume       → file_db/{username}/applications/{application_id}/resume.pdf
        cover_letter → file_db/{username}/applications/{application_id}/cover_letter.pdf
    """
    if document not in ("resume", "cover_letter"):
        raise ValueError("document must be 'resume' or 'cover_letter'")

    import markdown as md_lib
    import weasyprint

    md_content = read_application_file(username, application_id, f"{document}.md")
    if not md_content.strip():
        logger.warning("export_pdf called but %s.md is empty", document)
        return

    body_html = md_lib.markdown(md_content, extensions=["extra"])
    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.5; color: #111; }}
  h1 {{ font-size: 1.8em; border-bottom: 2px solid #333; padding-bottom: 4px; }}
  h2 {{ font-size: 1.3em; margin-top: 1.4em; border-bottom: 1px solid #ccc; }}
  h3 {{ font-size: 1.1em; margin-bottom: 0.2em; }}
  ul {{ padding-left: 1.5em; }}
  p, li {{ margin: 0.3em 0; }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""

    pdf_bytes = weasyprint.HTML(string=full_html).write_pdf()
    pdf_path = FILE_DB_PATH / username / "applications" / application_id / f"{document}.pdf"
    pdf_path.write_bytes(pdf_bytes)
