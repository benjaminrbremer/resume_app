import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import backend.db.crud.experience as crud
from backend.routers.schemas import (
    ExperienceCreate,
    ExperienceChatRequest,
    ExperienceUpdate,
)

router = APIRouter()


@router.post("/chat")
async def experience_chat(body: ExperienceChatRequest):
    from backend.llm.agent import run_experience_agent

    reply = await asyncio.to_thread(
        run_experience_agent,
        body.username,
        body.message,
        [m.model_dump() for m in body.history],
    )
    return JSONResponse(content={"reply": reply})


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
    return JSONResponse(status_code=201, content=record)


@router.get("/{exp_id}")
async def get_experience(exp_id: str):
    record = crud.get_experience(exp_id)
    if not record:
        raise HTTPException(status_code=404, detail="Experience not found")
    return JSONResponse(content=record)


@router.put("/{exp_id}")
async def update_experience(exp_id: str, body: ExperienceUpdate):
    record = crud.update_experience(exp_id, **body.model_dump(exclude_none=True))
    if not record:
        raise HTTPException(status_code=404, detail="Experience not found")
    return JSONResponse(content=record)


@router.delete("/{exp_id}")
async def delete_experience(exp_id: str):
    deleted = crud.delete_experience(exp_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Experience not found")
    return JSONResponse(content={"deleted": True})
