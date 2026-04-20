"""
Pydantic request and response models for all API routes.
"""

import re
from datetime import date

from pydantic import BaseModel, field_validator, model_validator

_DATE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _validate_dates(start_date: str | None, end_date: str | None) -> None:
    today = date.today().strftime("%Y-%m")
    if start_date and start_date > today:
        raise ValueError("start_date cannot be in the future")
    if end_date:
        if end_date > today:
            raise ValueError("end_date cannot be in the future")
        if not start_date:
            raise ValueError("start_date is required when end_date is set")
        if start_date > end_date:
            raise ValueError("end_date must be on or after start_date")


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

class ExperienceCreate(BaseModel):
    type: str  # general | job | project | volunteer
    title: str
    start_date: str | None = None
    end_date: str | None = None
    content: str | None = None

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: object) -> object:
        if v == "":
            return None
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> "ExperienceCreate":
        _validate_dates(self.start_date, self.end_date)
        return self


class ExperienceUpdate(BaseModel):
    type: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    content: str | None = None

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: object) -> object:
        if v == "":
            return None
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> "ExperienceUpdate":
        _validate_dates(self.start_date, self.end_date)
        return self


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

class SkillCreate(BaseModel):
    name: str
    proficiency: str | None = None
    content: str | None = None


class SkillUpdate(BaseModel):
    name: str | None = None
    proficiency: str | None = None
    content: str | None = None


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
    job_description: str | None = None
    website_url: str | None = None
    generate_resume: bool = False
    generate_cover_letter: bool = False


class ApplicationUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    job_description: str | None = None
    website_url: str | None = None
    outcome: str | None = None
    submitted_dt: str | None = None
    outcome_dt: str | None = None


class ChatMessageRequest(BaseModel):
    message: str
    username: str  # temporary until session auth is implemented


class GenerateDocumentRequest(BaseModel):
    username: str  # temporary until session auth is implemented


class SaveAndGenerateRequest(BaseModel):
    username: str
    selected_experience_ids: list[str]
    changes_prompt: str | None = None
    generate_resume: bool = False
    generate_cover_letter: bool = False
    title: str | None = None
    company: str | None = None
    website_url: str | None = None
    job_description: str | None = None


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

class UploadExampleRequest(BaseModel):
    username: str
    filename: str


class ExampleDocumentUpdate(BaseModel):
    document_type: str | None = None  # resume | cover_letter | other
