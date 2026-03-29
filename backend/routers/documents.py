from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/upload-example")
async def upload_example(username: str = Form(...), file: UploadFile = File(...)):
    return JSONResponse(status_code=501, content={"detail": "Not implemented"})
