from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.routers.schemas import LoginRequest, RegisterRequest

router = APIRouter()


@router.post("/register")
async def register(body: RegisterRequest):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.post("/login")
async def login(body: LoginRequest):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})
