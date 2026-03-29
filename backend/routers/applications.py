from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.routers.schemas import (
    ApplicationCreate,
    ApplicationUpdate,
    ChatMessageRequest,
    GenerateDocumentRequest,
)

router = APIRouter()


@router.get("/")
async def list_applications(username: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.post("/")
async def create_application(body: ApplicationCreate, username: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.get("/{app_id}")
async def get_application(app_id: str):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.put("/{app_id}")
async def update_application(app_id: str, body: ApplicationUpdate):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.post("/{app_id}/chat")
async def chat(app_id: str, body: ChatMessageRequest):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.post("/{app_id}/generate-resume")
async def generate_resume(app_id: str, body: GenerateDocumentRequest):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})


@router.post("/{app_id}/generate-cover-letter")
async def generate_cover_letter(app_id: str, body: GenerateDocumentRequest):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})
