"""
LLM-callable tools for researching external URLs (company websites, job postings).
"""


def research_url(url: str) -> str:
    """
    Fetch and summarize the content at the given URL.

    Intended to populate:
        - company_research.md (company website)
        - job_info.md (job posting page)

    Implementation will fetch the page content and pass it to the LLM
    to produce a structured markdown summary.

    Args:
        url: The URL to fetch and summarize.

    Returns:
        A markdown-formatted string containing the summarized content.
    """
    raise NotImplementedError
