from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import backend.db.crud.applications as crud
import backend.db.crud.experience as crud_experience
import backend.db.crud.jobs as crud_jobs
import backend.db.crud.skills as crud_skills
from backend.file_db.operations import read_application_file, write_application_file
from backend.llm.agent import run_agent
from backend.llm.generate import run_generation_pipeline, run_search_only_pipeline
from backend.routers.schemas import (
    ApplicationCreate,
    ApplicationUpdate,
    ChatMessageRequest,
    GenerateDocumentRequest,
    SaveAndGenerateRequest,
)
from backend.tools.documents import export_pdf, generate_cover_letter, generate_resume
from backend.tools.research import run_research_pipeline
from backend.tools.experience import search_experience
from backend.utils import parse_relevant_uuids

router = APIRouter()


def _format_job_info(title: str, company: str, website_url: str | None, job_description: str | None) -> str:
    lines = [
        "# Job Information",
        "",
        f"**Role:** {title}",
        f"**Company:** {company}",
        f"**Website:** {website_url or 'N/A'}",
        "",
        "## Job Description",
        "",
        job_description or "",
    ]
    return "\n".join(lines)


@router.get("/")
async def list_applications(username: str):
    records = crud.get_applications_for_user(username)
    return JSONResponse(content=records)


@router.post("/")
async def create_application(body: ApplicationCreate, username: str):
    record = crud.create_application(username=username, title=body.title, company=body.company)
    if body.website_url:
        crud.update_application(record["id"], website_url=body.website_url)
    job_info_md = _format_job_info(body.title, body.company, body.website_url, body.job_description)
    write_application_file(username, record["id"], "job_info.md", job_info_md)

    app_id = record["id"]

    if body.generate_resume or body.generate_cover_letter:
        run_research_pipeline(
            username=username,
            application_id=app_id,
            company_name=body.company,
            job_title=body.title,
            website_url=body.website_url,
        )
        search_experience(username, app_id)
        if body.generate_resume:
            generate_resume(username, app_id)
            export_pdf(username, app_id, "resume")
        if body.generate_cover_letter:
            generate_cover_letter(username, app_id)
            export_pdf(username, app_id, "cover_letter")
    else:
        run_search_only_pipeline(username, app_id)

    return JSONResponse(status_code=201, content={
        **crud.get_application(app_id),
        "job_description": body.job_description or "",
    })


@router.get("/{app_id}/documents")
async def get_application_documents(app_id: str):
    record = crud.get_application(app_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")
    username = record["username"]
    resume_md = read_application_file(username, app_id, "resume.md")
    cover_letter_md = read_application_file(username, app_id, "cover_letter.md")
    return JSONResponse(content={
        "resume_markdown": resume_md,
        "cover_letter_markdown": cover_letter_md,
    })


@router.get("/{app_id}/experience")
async def get_application_experience(app_id: str):
    record = crud.get_application(app_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")
    username = record["username"]

    relevant_md = read_application_file(username, app_id, "relevant_experience.md")
    selected_ids = set(parse_relevant_uuids(relevant_md))

    experience = []
    for item in crud_experience.get_experience_for_user(username):
        experience.append({**item, "selected": item["id"] in selected_ids})

    jobs = []
    for item in crud_jobs.get_jobs_for_user(username):
        jobs.append({**item, "selected": item["id"] in selected_ids})

    skills = []
    for item in crud_skills.get_skills_for_user(username):
        skills.append({**item, "selected": item["id"] in selected_ids})

    return JSONResponse(content={
        "experience": experience,
        "jobs": jobs,
        "skills": skills,
    })


@router.get("/{app_id}")
async def get_application(app_id: str):
    record = crud.get_application(app_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")
    job_info_md = read_application_file(record["username"], app_id, "job_info.md")
    job_description = ""
    if "## Job Description" in job_info_md:
        job_description = job_info_md.split("## Job Description", 1)[1].strip()
    return JSONResponse(content={**record, "job_description": job_description})


@router.put("/{app_id}")
async def update_application(app_id: str, body: ApplicationUpdate):
    record = crud.get_application(app_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")

    db_fields = body.model_dump(exclude_none=True, exclude={"job_description"})
    if db_fields:
        record = crud.update_application(app_id, **db_fields)

    # Rewrite job_info.md if any of its fields changed
    if body.job_description is not None or body.title is not None or body.company is not None or body.website_url is not None:
        current_record = crud.get_application(app_id)
        current_job_info = read_application_file(current_record["username"], app_id, "job_info.md")
        current_description = ""
        if "## Job Description" in current_job_info:
            current_description = current_job_info.split("## Job Description", 1)[1].strip()
        new_description = body.job_description if body.job_description is not None else current_description
        job_info_md = _format_job_info(
            current_record["title"],
            current_record["company"],
            current_record.get("website_url"),
            new_description,
        )
        write_application_file(current_record["username"], app_id, "job_info.md", job_info_md)
        return JSONResponse(content={**current_record, "job_description": new_description})

    return JSONResponse(content=record)


@router.post("/{app_id}/save-and-generate")
async def save_and_generate(app_id: str, body: SaveAndGenerateRequest):
    record = crud.get_application(app_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")

    username = body.username

    # Save job info fields if any were provided
    db_update_fields = {}
    if body.title is not None:
        db_update_fields["title"] = body.title
    if body.company is not None:
        db_update_fields["company"] = body.company
    if body.website_url is not None:
        db_update_fields["website_url"] = body.website_url
    if db_update_fields:
        crud.update_application(app_id, **db_update_fields)

    # Rewrite job_info.md if any job info field provided
    if body.title is not None or body.company is not None or body.website_url is not None or body.job_description is not None:
        current_record = crud.get_application(app_id)
        current_job_info = read_application_file(username, app_id, "job_info.md")
        current_description = ""
        if "## Job Description" in current_job_info:
            current_description = current_job_info.split("## Job Description", 1)[1].strip()
        new_description = body.job_description if body.job_description is not None else current_description
        job_info_md = _format_job_info(
            current_record["title"],
            current_record["company"],
            current_record.get("website_url"),
            new_description,
        )
        write_application_file(username, app_id, "job_info.md", job_info_md)

    # Write selected experience IDs to relevant_experience.md
    lines = ["# Relevant Experience", "", "<!-- UUIDs selected for this application -->"]
    for uid in body.selected_experience_ids:
        lines.append(f"- {uid} | manually selected | score: 1.000")
    write_application_file(username, app_id, "relevant_experience.md", "\n".join(lines))

    result = {"resume_markdown": None, "cover_letter_markdown": None}

    if body.generate_resume or body.generate_cover_letter:
        current_record = crud.get_application(app_id)
        run_research_pipeline(
            username=username,
            application_id=app_id,
            company_name=current_record["company"],
            job_title=current_record["title"],
            website_url=current_record.get("website_url"),
        )
        if body.generate_resume:
            generate_resume(username, app_id, changes_prompt=body.changes_prompt)
            export_pdf(username, app_id, "resume")
            result["resume_markdown"] = read_application_file(username, app_id, "resume.md")
        if body.generate_cover_letter:
            generate_cover_letter(username, app_id, changes_prompt=body.changes_prompt)
            export_pdf(username, app_id, "cover_letter")
            result["cover_letter_markdown"] = read_application_file(username, app_id, "cover_letter.md")

    return JSONResponse(content=result)


@router.post("/{app_id}/generate-resume")
async def generate_resume_endpoint(app_id: str, body: GenerateDocumentRequest):
    record = crud.get_application(app_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")
    markdown_content = run_generation_pipeline(body.username, app_id, "resume")
    return JSONResponse(content={"markdown": markdown_content})


@router.post("/{app_id}/generate-cover-letter")
async def generate_cover_letter_endpoint(app_id: str, body: GenerateDocumentRequest):
    record = crud.get_application(app_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")
    markdown_content = run_generation_pipeline(body.username, app_id, "cover_letter")
    return JSONResponse(content={"markdown": markdown_content})


@router.post("/{app_id}/chat")
async def chat(app_id: str, body: ChatMessageRequest):
    record = crud.get_application(app_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")
    response_text = run_agent(body.username, app_id, body.message)
    return JSONResponse(content={"response": response_text})
