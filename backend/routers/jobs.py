from fastapi import APIRouter
from fastapi.responses import JSONResponse

import backend.db.crud.jobs as crud
from backend.routers.schemas import JobCreate, JobUpdate

router = APIRouter()


@router.get("/")
async def list_jobs(username: str):
    records = crud.get_jobs_for_user(username)
    return JSONResponse(content=records)


@router.post("/")
async def create_job(body: JobCreate, username: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.get("/{job_id}")
async def get_job(job_id: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.put("/{job_id}")
async def update_job(job_id: str, body: JobUpdate):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})
