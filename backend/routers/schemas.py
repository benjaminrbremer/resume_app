"""
Pydantic request and response models for all API routes.
"""

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    username: str
    password: str
    firstname: str | None = None
    lastname: str | None = None
    linkedin_url: str | None = None
    profile_url: str | None = None
    github_url: str | None = None
    email: str | None = None
    phone: str | None = None
    objective: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    message: str


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

class ExperienceChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ExperienceChatRequest(BaseModel):
    username: str  # temporary until session auth is implemented
    message: str
    history: list[ExperienceChatMessage] = []


class ExperienceChatResponse(BaseModel):
    reply: str


class ExperienceCreate(BaseModel):
    type: str  # general | job_project | personal
    title: str
    start_date: str | None = None
    end_date: str | None = None


class ExperienceUpdate(BaseModel):
    type: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

class SkillCreate(BaseModel):
    name: str
    proficiency: str | None = None


class SkillUpdate(BaseModel):
    name: str | None = None
    proficiency: str | None = None


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

class JobCreate(BaseModel):
    title: str
    company: str
    start_date: str | None = None
    end_date: str | None = None


class JobUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    start_date: str | None = None
    end_date: str | None = None


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

class ApplicationCreate(BaseModel):
    title: str
    company: str


class ApplicationUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    outcome: str | None = None
    submitted_dt: str | None = None
    outcome_dt: str | None = None


class ChatMessageRequest(BaseModel):
    message: str
    username: str  # temporary until session auth is implemented


class GenerateDocumentRequest(BaseModel):
    username: str  # temporary until session auth is implemented


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

class UploadExampleRequest(BaseModel):
    username: str
    filename: str
