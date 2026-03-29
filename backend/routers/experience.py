from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.routers.schemas import ExperienceCreate, ExperienceUpdate

router = APIRouter()


@router.get("/")
async def list_experience(username: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.post("/")
async def create_experience(body: ExperienceCreate, username: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.get("/{exp_id}")
async def get_experience(exp_id: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.put("/{exp_id}")
async def update_experience(exp_id: str, body: ExperienceUpdate):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.delete("/{exp_id}")
async def delete_experience(exp_id: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})
