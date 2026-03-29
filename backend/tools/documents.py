"""
LLM-callable tools for generating and exporting resume/cover letter documents.
"""


def generate_resume(username: str, application_id: str) -> None:
    """
    Generate a tailored resume in markdown format for the given application.

    Uses the following inputs from the file DB:
        - file_db/{username}/user_info.md
        - file_db/{username}/applications/{application_id}/relevant_experience.md
        - file_db/{username}/applications/{application_id}/job_info.md
        - file_db/{username}/example_documents/ (for style/voice reference)

    Writes the result to:
        file_db/{username}/applications/{application_id}/resume.md

    Args:
        username: The authenticated user.
        application_id: UUID of the application being tailored.
    """
    raise NotImplementedError


def generate_cover_letter(username: str, application_id: str) -> None:
    """
    Generate a tailored cover letter in markdown format for the given application.

    Uses the following inputs from the file DB:
        - file_db/{username}/applications/{application_id}/resume.md
        - file_db/{username}/applications/{application_id}/job_info.md
        - file_db/{username}/applications/{application_id}/company_research.md
        - file_db/{username}/example_documents/ (for style/voice reference)

    Writes the result to:
        file_db/{username}/applications/{application_id}/cover_letter.md

    Args:
        username: The authenticated user.
        application_id: UUID of the application being tailored.
    """
    raise NotImplementedError


def export_pdf(username: str, application_id: str, document: str) -> None:
    """
    Convert a markdown document to PDF and save it alongside the source file.

    Reads the markdown source and writes a PDF to the same application directory.

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
    raise NotImplementedError
