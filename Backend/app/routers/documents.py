from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile

from app.dependencies import get_current_user
from app.models.user import User
from app.models.document import UploadedDocument
from app.schemas.document import DocumentPublic, UploadResponse
from app.services.document_service import list_documents_for_user, save_upload
from app.services.ingestion_service import run_ingestion


router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_document(
    background:BackgroundTasks,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    try:
        doc = await save_upload(file, str(user.id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    background.add_task(run_ingestion, str(doc.id))
    return {
        "message": "File uploaded",
        "document": DocumentPublic(
            id=str(doc.id),
            filename=doc.filename,
            size=doc.size,
            source_type=doc.source_type,
            status=doc.status,
            uploaded_at=doc.uploaded_at,
        ),
    }


@router.get("", response_model=list[DocumentPublic])
async def list_documents(user: User = Depends(get_current_user)):
    docs = await list_documents_for_user(str(user.id))
    return [
        DocumentPublic(
            id=str(d.id),
            filename=d.filename,
            size=d.size,
            source_type=d.source_type,
            status=d.status,
            uploaded_at=d.uploaded_at,
        )
        for d in docs
    ]


@router.get("/{document_id}",response_model=DocumentPublic)
async def get_document(
    document_id: str,
    user: User = Depends(get_current_user),
):
    doc=await UploadedDocument.get(document_id)
    if not doc or doc.uploaded_by != str(user.id):
        raise HTTPException(status_code=404,detail="Error with the document processing")
    
    return DocumentPublic(
        id=str(doc.id),
        filename=doc.filename,
        size=doc.size,
        source_type=doc.source_type,
        status=doc.status,
        uploaded_at=doc.uploaded_at,
    )