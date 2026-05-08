"""
LLM-callable tools for managing experience data.
"""


def search_experience(username: str, application_id: str) -> None:
    """
    Select and rank the user's most relevant experience entries for a job application.

    Reads all experience markdown files for the user, plus job_info.md and
    company_research.md for the given application. Calls the LLM to rank and
    select the most relevant experience IDs, then writes the result to
    relevant_experience.md for the application.

    Args:
        username: The authenticated user's username.
        application_id: UUID of the target application.
    """
    raise NotImplementedError
