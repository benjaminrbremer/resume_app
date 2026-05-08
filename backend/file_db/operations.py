"""
All file DB read/write operations.

This is the single source of truth for file path construction.
No other module should build file_db paths directly.

Directory layout:
    file_db/
        {username}/
            user_info.md
            experience/
                {id}.md     <- experience, jobs, AND skills share this dir (UUIDs are globally unique)
            applications/
                {app_id}/
                    resume.md
                    resume.pdf
                    cover_letter.md
                    cover_letter.pdf
                    company_research.md
                    job_info.md
                    relevant_experience.md
            example_documents/
                {filename}
"""

from pathlib import Path

from backend.config import FILE_DB_PATH

# ---------------------------------------------------------------------------
# Internal path helpers
# ---------------------------------------------------------------------------

def _user_root(username: str) -> Path:
    return FILE_DB_PATH / username


def _user_info_path(username: str) -> Path:
    return _user_root(username) / "user_info.md"


def _experience_dir(username: str) -> Path:
    return _user_root(username) / "experience"


def _experience_path(username: str, item_id: str) -> Path:
    return _experience_dir(username) / f"{item_id}.md"


def _applications_dir(username: str) -> Path:
    return _user_root(username) / "applications"


def _application_dir(username: str, app_id: str) -> Path:
    return _applications_dir(username) / app_id


def _application_file(username: str, app_id: str, filename: str) -> Path:
    return _application_dir(username, app_id) / filename


def _example_docs_dir(username: str) -> Path:
    return _user_root(username) / "example_documents"


# ---------------------------------------------------------------------------
# User-level operations
# ---------------------------------------------------------------------------

def init_user_directories(username: str) -> None:
    """
    Create the full directory structure for a new user and seed an empty user_info.md.
    Safe to call multiple times (idempotent).
    """
    _experience_dir(username).mkdir(parents=True, exist_ok=True)
    _applications_dir(username).mkdir(parents=True, exist_ok=True)
    _example_docs_dir(username).mkdir(parents=True, exist_ok=True)

    info_path = _user_info_path(username)
    if not info_path.exists():
        info_path.write_text("", encoding="utf-8")


def read_user_info(username: str) -> str:
    """Return the contents of user_info.md, or empty string if not found."""
    path = _user_info_path(username)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_user_info(username: str, content: str) -> None:
    """Overwrite user_info.md with the given content."""
    _user_info_path(username).write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Experience / job / skill file operations (shared experience/ directory)
# ---------------------------------------------------------------------------

def read_experience_file(username: str, item_id: str) -> str:
    """
    Return the markdown content for a given experience/job/skill ID.
    Returns empty string if the file does not exist yet.
    """
    path = _experience_path(username, item_id)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_experience_file(username: str, item_id: str, content: str) -> None:
    """Write (or overwrite) the markdown file for a given experience/job/skill ID."""
    _experience_path(username, item_id).write_text(content, encoding="utf-8")


def delete_experience_file(username: str, item_id: str) -> None:
    """Delete the markdown file for a given ID. No-op if the file does not exist."""
    path = _experience_path(username, item_id)
    if path.exists():
        path.unlink()


def list_experience_ids(username: str) -> list[str]:
    """
    Return all experience/job/skill IDs for a user by scanning filenames
    in the experience/ directory. Returns UUIDs (filename stems).
    """
    exp_dir = _experience_dir(username)
    if not exp_dir.exists():
        return []
    return [p.stem for p in exp_dir.glob("*.md")]


# ---------------------------------------------------------------------------
# Application file operations
# ---------------------------------------------------------------------------

_APPLICATION_SEED_FILES = [
    "resume.md",
    "cover_letter.md",
    "company_research.md",
    "job_info.md",
    "relevant_experience.md",
]


def init_application_directory(username: str, app_id: str) -> None:
    """
    Create the application subdirectory and seed all required markdown files as empty.
    Safe to call multiple times (idempotent).
    """
    app_dir = _application_dir(username, app_id)
    app_dir.mkdir(parents=True, exist_ok=True)

    for filename in _APPLICATION_SEED_FILES:
        file_path = app_dir / filename
        if not file_path.exists():
            file_path.write_text("", encoding="utf-8")


def read_application_file(username: str, app_id: str, filename: str) -> str:
    """
    Return the contents of a file within an application directory.
    Returns empty string if the file does not exist.
    """
    path = _application_file(username, app_id, filename)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_application_file(username: str, app_id: str, filename: str, content: str) -> None:
    """Write (or overwrite) a file within an application directory."""
    _application_file(username, app_id, filename).write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Example document operations
# ---------------------------------------------------------------------------

def save_example_document(username: str, doc_id: str, data: bytes) -> None:
    """Save an uploaded example document to the example_documents directory, keyed by doc_id."""
    dest = _example_docs_dir(username) / doc_id
    dest.write_bytes(data)


def read_example_document(username: str, doc_id: str) -> bytes:
    """Return the raw bytes of an example document. Returns empty bytes if not found."""
    path = _example_docs_dir(username) / doc_id
    if not path.exists():
        return b""
    return path.read_bytes()


def delete_example_document(username: str, doc_id: str) -> None:
    """Delete an example document file. No-op if the file does not exist."""
    path = _example_docs_dir(username) / doc_id
    if path.exists():
        path.unlink()


def list_example_documents(username: str) -> list[str]:
    """Return doc_ids of all uploaded example documents for a user."""
    docs_dir = _example_docs_dir(username)
    if not docs_dir.exists():
        return []
    return [p.name for p in docs_dir.iterdir() if p.is_file()]
