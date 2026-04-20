"""
Tools for researching external URLs (company websites, job postings) and
running a full company research pipeline.
"""

import logging
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from backend.file_db.operations import write_application_file
from backend.llm.client import VLLMClient

logger = logging.getLogger(__name__)

_CRAWL_KEYWORDS = {"about", "mission", "team", "careers", "culture", "values", "story", "who-we-are"}
_MAX_WEBSITE_PAGES = 5
_MAX_SEARCH_PAGES = 8
_MAX_CHARS_PER_PAGE = 3000
_MAX_TOTAL_CHARS = 12000


def research_url(url: str) -> str:
    """
    Fetch a single URL and return its extracted text content (LLM-callable tool).

    Args:
        url: The URL to fetch.

    Returns:
        Extracted plain text from the page, truncated to ~3000 chars.
    """
    try:
        response = httpx.get(url, timeout=15.0, follow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0 (compatible; ResumeBot/1.0)"})
        response.raise_for_status()
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    texts = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = tag.get_text(separator=" ", strip=True)
        if len(text) > 30:
            texts.append(text)

    combined = "\n".join(texts)
    return combined[:_MAX_CHARS_PER_PAGE]


def _find_relevant_links(base_url: str, html: str) -> list[str]:
    """Return internal links whose path contains a crawl keyword."""
    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url).netloc
    found = []
    seen = set()
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        full = urljoin(base_url, href)
        parsed = urlparse(full)
        if parsed.netloc != base_domain:
            continue
        path = parsed.path.lower()
        if any(kw in path for kw in _CRAWL_KEYWORDS) and full not in seen:
            seen.add(full)
            found.append(full)
    return found


def run_research_pipeline(
    username: str,
    application_id: str,
    company_name: str,
    job_title: str,
    website_url: str | None,
) -> str:
    """
    Run the full company research pipeline for a job application.

    Steps:
    1. Crawl the company website (if provided) for About/Mission/Culture pages.
    2. Search the web for hiring process, culture, and interview info.
    3. Distill all raw content via LLM into a structured markdown report.
    4. Write the report to company_research.md under the application.

    Args:
        username: The authenticated user.
        application_id: UUID of the application.
        company_name: Company name for search queries.
        job_title: Job title for search queries.
        website_url: Optional base URL of the employer's website.

    Returns:
        The distilled research markdown string.
    """
    collected: list[str] = []
    pages_fetched = 0

    # Step 1: Crawl company website
    if website_url:
        try:
            base_response = httpx.get(
                website_url, timeout=15.0, follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (compatible; ResumeBot/1.0)"}
            )
            base_text = research_url(website_url)
            if base_text:
                collected.append(f"## {website_url}\n{base_text}")
                pages_fetched += 1

            relevant_links = _find_relevant_links(website_url, base_response.text)
            for link in relevant_links:
                if pages_fetched >= _MAX_WEBSITE_PAGES:
                    break
                text = research_url(link)
                if text:
                    collected.append(f"## {link}\n{text}")
                    pages_fetched += 1
        except Exception as exc:
            logger.warning("Website crawl failed for %s: %s", website_url, exc)

    # Step 2: Web searches via DuckDuckGo
    search_queries = [
        f"{company_name} {job_title} interview process",
        f"{company_name} work culture values",
        f"{company_name} {job_title} hiring what to expect",
    ]
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for query in search_queries:
                if pages_fetched >= _MAX_WEBSITE_PAGES + _MAX_SEARCH_PAGES:
                    break
                results = list(ddgs.text(query, max_results=3))
                for result in results:
                    if pages_fetched >= _MAX_WEBSITE_PAGES + _MAX_SEARCH_PAGES:
                        break
                    url = result.get("href") or result.get("url", "")
                    if not url:
                        continue
                    text = research_url(url)
                    if text:
                        collected.append(f"## {url}\n{text}")
                        pages_fetched += 1
    except Exception as exc:
        logger.warning("Web search failed: %s", exc)

    if not collected:
        report = f"No research data could be collected for {company_name} — {job_title}."
        write_application_file(username, application_id, "company_research.md", report)
        return report

    # Step 3: Distill via LLM
    raw_text = "\n\n".join(collected)
    if len(raw_text) > _MAX_TOTAL_CHARS:
        raw_text = raw_text[:_MAX_TOTAL_CHARS]

    client = VLLMClient()
    system_prompt = (
        "You are a research assistant helping a job applicant prepare for an application. "
        "Summarize the following scraped web content into a concise, structured markdown report. "
        "Cover: (1) what the company does and their products/services, (2) company values and culture, "
        "(3) the role's likely responsibilities based on what you know, "
        "(4) what the hiring process looks like. "
        "Be specific and factual. Do not repeat yourself. Output only the report in markdown."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Company: {company_name}\nRole: {job_title}\n\n---\n\n{raw_text}"},
    ]
    response = client.chat(messages, tools=None)
    report = response["choices"][0]["message"]["content"].strip()

    write_application_file(username, application_id, "company_research.md", report)
    return report
