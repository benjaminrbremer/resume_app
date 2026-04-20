"""
Deterministic document generation pipeline.

Runs research → experience search → document generation → PDF export
in a fixed sequence. Does not use an agentic LLM loop — steps always
execute in order for reliability.
"""

from typing import Literal

from backend.db.crud.applications import get_application
from backend.file_db.operations import read_application_file, write_application_file
from backend.tools.documents import export_pdf, generate_cover_letter, generate_resume
from backend.tools.experience import search_experience
from backend.tools.research import run_research_pipeline


def run_search_only_pipeline(username: str, application_id: str) -> None:
    """
    Run research and vector experience search without generating any documents.

    Used at application creation time when no document generation is requested,
    so the detail page can immediately show pre-selected relevant experience.

    Args:
        username: The authenticated user.
        application_id: UUID of the target application.
    """
    app = get_application(application_id)
    if not app:
        raise ValueError(f"Application {application_id} not found")

    run_research_pipeline(
        username=username,
        application_id=application_id,
        company_name=app["company"],
        job_title=app["title"],
        website_url=app.get("website_url"),
    )

    search_experience(username, application_id)


def run_generation_pipeline(
    username: str,
    application_id: str,
    document_type: Literal["resume", "cover_letter"],
    selected_ids: list[str] | None = None,
    changes_prompt: str | None = None,
) -> str:
    """
    Run the full document generation pipeline for a job application.

    Steps (always in this order):
        1. Load application metadata (company, title, website_url).
        2. Run company research pipeline (website crawl + web search + distillation).
        3. Select experience: if selected_ids is provided, write them directly to
           relevant_experience.md (skipping vector search). Otherwise run vector search.
        4. Generate the requested document (resume or cover letter) via LLM.
        5. Export the document to PDF.

    Args:
        username: The authenticated user.
        application_id: UUID of the target application.
        document_type: Which document to generate — 'resume' or 'cover_letter'.
        selected_ids: If provided, use these UUIDs as the relevant experience set
            instead of running vector search.
        changes_prompt: Optional additional instructions injected into the LLM prompt.

    Returns:
        The generated markdown content (also written to file DB).
    """
    app = get_application(application_id)
    if not app:
        raise ValueError(f"Application {application_id} not found")

    run_research_pipeline(
        username=username,
        application_id=application_id,
        company_name=app["company"],
        job_title=app["title"],
        website_url=app.get("website_url"),
    )

    if selected_ids is not None:
        lines = ["# Relevant Experience", "", "<!-- UUIDs selected for this application -->"]
        for uid in selected_ids:
            lines.append(f"- {uid} | manually selected | score: 1.000")
        write_application_file(username, application_id, "relevant_experience.md", "\n".join(lines))
    else:
        search_experience(username, application_id)

    if document_type == "resume":
        generate_resume(username, application_id, changes_prompt=changes_prompt)
    else:
        generate_cover_letter(username, application_id, changes_prompt=changes_prompt)

    export_pdf(username, application_id, document_type)

    return read_application_file(username, application_id, f"{document_type}.md")
