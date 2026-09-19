import uuid
from pathlib import Path

from fastapi import UploadFile

from app.models.document import UploadedDocument


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


async def save_upload(file: UploadFile, user_id: str) -> UploadedDocument:
    original_name = file.filename or "unnamed"
    ext = Path(original_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = UPLOAD_DIR / stored_name

    content = await file.read()
    stored_path.write_bytes(content)

    doc = UploadedDocument(
        filename=original_name,
        stored_path=str(stored_path),
        size=len(content),
        source_type=ext.lstrip("."),
        status="pending",
        uploaded_by=user_id,
    )
    await doc.insert()
    return doc


async def list_documents_for_user(user_id: str) -> list[UploadedDocument]:
    return (
        await UploadedDocument.find(UploadedDocument.uploaded_by == user_id)
        .sort(-UploadedDocument.uploaded_at)
        .to_list()
    )