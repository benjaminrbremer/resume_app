from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.routers.schemas import JobCreate, JobUpdate

router = APIRouter()


@router.get("/")
async def list_jobs(username: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


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
