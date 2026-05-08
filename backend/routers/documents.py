from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response

import backend.db.crud.documents as crud
from backend.file_db.operations import (
    delete_example_document as delete_example_document_file,
    read_example_document,
    save_example_document,
)
from backend.routers.schemas import ExampleDocumentUpdate

router = APIRouter()


@router.post("/upload-example")
async def upload_example(username: str = Form(...), file: UploadFile = File(...)):
    data = await file.read()
    record = crud.create_example_document(
        username=username,
        original_filename=file.filename or "untitled",
        content_type=file.content_type,
    )
    save_example_document(username, record["id"], data)
    return JSONResponse(status_code=201, content=record)


@router.get("/example-documents")
async def list_example_documents(username: str):
    records = crud.get_example_documents_for_user(username)
    return JSONResponse(content=records)


@router.get("/example-documents/{doc_id}/content")
async def get_example_document_content(doc_id: str, download: bool = False):
    record = crud.get_example_document(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    data = read_example_document(record["username"], doc_id)
    if not data:
        raise HTTPException(status_code=404, detail="File not found")
    content_type = record["content_type"] or "application/octet-stream"
    filename = record["original_filename"]
    disposition = (
        f'attachment; filename="{filename}"' if download else f'inline; filename="{filename}"'
    )
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": disposition},
    )


@router.put("/example-documents/{doc_id}")
async def update_example_document(doc_id: str, body: ExampleDocumentUpdate):
    record = crud.update_example_document(doc_id, **body.model_dump(exclude_none=True))
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return JSONResponse(content=record)


@router.delete("/example-documents/{doc_id}")
async def delete_example_document(doc_id: str):
    record = crud.get_example_document(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_example_document_file(record["username"], doc_id)
    crud.delete_example_document(doc_id)
    return JSONResponse(content={"deleted": True})
