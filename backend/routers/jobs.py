from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import backend.db.crud.jobs as crud
from backend.file_db.operations import (
    delete_experience_file,
    read_experience_file,
    write_experience_file,
)
from backend.llm.embeddings import try_generate_summary_and_embedding
from backend.routers.schemas import JobCreate, JobUpdate

router = APIRouter()


@router.get("/")
async def list_jobs(username: str):
    records = crud.get_jobs_for_user(username)
    return JSONResponse(content=records)


@router.post("/")
async def create_job(body: JobCreate, username: str):
    record = crud.create_job(
        username=username,
        title=body.title,
        company=body.company,
        start_date=body.start_date,
        end_date=body.end_date,
    )
    content = body.content or ""
    if body.content is not None:
        write_experience_file(username, record["id"], body.content)
    label = f"job: {record['title']} at {record['company']}"
    summary, embedding = try_generate_summary_and_embedding(label, content)
    if summary is not None:
        crud.update_job(record["id"], summary=summary, embedding=embedding)
    return JSONResponse(status_code=201, content=crud.get_job(record["id"]))


@router.get("/{job_id}")
async def get_job(job_id: str):
    record = crud.get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
    content = read_experience_file(record["username"], job_id)
    return JSONResponse(content={**record, "content": content})


@router.put("/{job_id}")
async def update_job(job_id: str, body: JobUpdate):
    db_fields = body.model_dump(exclude_none=True, exclude={"content"})
    record = crud.update_job(job_id, **db_fields)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
    if body.content is not None:
        write_experience_file(record["username"], job_id, body.content)
    content = body.content if body.content is not None else read_experience_file(record["username"], job_id)
    label = f"job: {record['title']} at {record['company']}"
    summary, embedding = try_generate_summary_and_embedding(label, content)
    if summary is not None:
        crud.update_job(job_id, summary=summary, embedding=embedding)
    return JSONResponse(content=crud.get_job(job_id))


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    record = crud.get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
    delete_experience_file(record["username"], job_id)
    crud.delete_job(job_id)
    return JSONResponse(content={"deleted": True})
