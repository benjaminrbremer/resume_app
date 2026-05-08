import sqlite3

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import backend.db.crud.users as crud
from backend.routers.schemas import LoginRequest, RegisterRequest

router = APIRouter()


@router.post("/register", status_code=201)
async def register(body: RegisterRequest):
    try:
        user = crud.create_user(
            body.username,
            body.password,
            firstname=body.firstname,
            lastname=body.lastname,
            linkedin_url=body.linkedin_url,
            profile_url=body.profile_url,
            github_url=body.github_url,
            email=body.email,
            phone=body.phone,
            objective=body.objective,
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Username already taken")
    return JSONResponse(status_code=201, content=user)


@router.post("/login")
async def login(body: LoginRequest):
    if not crud.verify_password(body.username, body.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return JSONResponse(content={"username": body.username, "message": "Login successful"})
