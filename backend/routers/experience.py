from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import backend.db.crud.experience as crud
from backend.file_db.operations import (
    delete_experience_file,
    read_experience_file,
    write_experience_file,
)
from backend.routers.schemas import ExperienceCreate, ExperienceUpdate

router = APIRouter()


@router.get("/")
async def list_experience(username: str):
    records = crud.get_experience_for_user(username)
    return JSONResponse(content=records)


@router.post("/")
async def create_experience(body: ExperienceCreate, username: str):
    record = crud.create_experience(
        username=username,
        type=body.type,
        title=body.title,
        start_date=body.start_date,
        end_date=body.end_date,
    )
    if body.content is not None:
        write_experience_file(username, record["id"], body.content)
    return JSONResponse(status_code=201, content=record)


@router.get("/{exp_id}")
async def get_experience(exp_id: str):
    record = crud.get_experience(exp_id)
    if not record:
        raise HTTPException(status_code=404, detail="Experience not found")
    content = read_experience_file(record["username"], exp_id)
    return JSONResponse(content={**record, "content": content})


@router.put("/{exp_id}")
async def update_experience(exp_id: str, body: ExperienceUpdate):
    record = crud.update_experience(exp_id, **body.model_dump(exclude_none=True))
    if not record:
        raise HTTPException(status_code=404, detail="Experience not found")
    if body.content is not None:
        write_experience_file(record["username"], exp_id, body.content)
    return JSONResponse(content=record)


@router.delete("/{exp_id}")
async def delete_experience(exp_id: str):
    record = crud.get_experience(exp_id)
    if not record:
        raise HTTPException(status_code=404, detail="Experience not found")
    delete_experience_file(record["username"], exp_id)
    crud.delete_experience(exp_id)
    return JSONResponse(content={"deleted": True})
