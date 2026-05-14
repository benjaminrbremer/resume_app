from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import backend.db.crud.skills as crud
from backend.file_db.operations import (
    delete_experience_file,
    read_experience_file,
    write_experience_file,
)
from backend.llm.embeddings import try_generate_summary_and_embedding
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
    content = body.content or ""
    if body.content is not None:
        write_experience_file(username, record["id"], body.content)
    proficiency_str = f" ({record['proficiency']})" if record.get("proficiency") else ""
    label = f"skill: {record['name']}{proficiency_str}"
    summary, embedding = try_generate_summary_and_embedding(label, content)
    if summary is not None:
        crud.update_skill(record["id"], summary=summary, embedding=embedding)
    return JSONResponse(status_code=201, content=crud.get_skill(record["id"]))


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
    content = body.content if body.content is not None else read_experience_file(record["username"], skill_id)
    proficiency_str = f" ({record['proficiency']})" if record.get("proficiency") else ""
    label = f"skill: {record['name']}{proficiency_str}"
    summary, embedding = try_generate_summary_and_embedding(label, content)
    if summary is not None:
        crud.update_skill(skill_id, summary=summary, embedding=embedding)
    return JSONResponse(content=crud.get_skill(skill_id))


@router.delete("/{skill_id}")
async def delete_skill(skill_id: str):
    record = crud.get_skill(skill_id)
    if not record:
        raise HTTPException(status_code=404, detail="Skill not found")
    delete_experience_file(record["username"], skill_id)
    crud.delete_skill(skill_id)
    return JSONResponse(content={"deleted": True})
