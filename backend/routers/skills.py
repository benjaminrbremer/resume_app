from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.routers.schemas import SkillCreate, SkillUpdate

router = APIRouter()


@router.get("/")
async def list_skills(username: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.post("/")
async def create_skill(body: SkillCreate, username: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.put("/{skill_id}")
async def update_skill(skill_id: str, body: SkillUpdate):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.delete("/{skill_id}")
async def delete_skill(skill_id: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})
