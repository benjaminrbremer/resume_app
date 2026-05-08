from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import backend.db.crud.skills as crud
from backend.file_db.operations import (
    delete_experience_file,
    read_experience_file,
    write_experience_file,
)
from backend.routers.schemas import SkillCreate, SkillUpdate

router = APIRouter()


@router.get("/")
async def list_skills(username: str):
    records = crud.get_skills_for_user(username)
    return JSONResponse(content=records)


@router.post("/")
async def create_skill(body: SkillCreate, username: str):
    record = crud.create_skill(
        username=username,
        name=body.name,
        proficiency=body.proficiency,
    )
    if body.content is not None:
        write_experience_file(username, record["id"], body.content)
    return JSONResponse(status_code=201, content=record)


@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    record = crud.get_skill(skill_id)
    if not record:
        raise HTTPException(status_code=404, detail="Skill not found")
    content = read_experience_file(record["username"], skill_id)
    return JSONResponse(content={**record, "content": content})


@router.put("/{skill_id}")
async def update_skill(skill_id: str, body: SkillUpdate):
    record = crud.update_skill(skill_id, **body.model_dump(exclude_none=True))
    if not record:
        raise HTTPException(status_code=404, detail="Skill not found")
    if body.content is not None:
        write_experience_file(record["username"], skill_id, body.content)
    return JSONResponse(content=record)


@router.delete("/{skill_id}")
async def delete_skill(skill_id: str):
    record = crud.get_skill(skill_id)
    if not record:
        raise HTTPException(status_code=404, detail="Skill not found")
    delete_experience_file(record["username"], skill_id)
    crud.delete_skill(skill_id)
    return JSONResponse(content={"deleted": True})
