from datetime import datetime

from beanie import Document
from pydantic import Field
from pymongo import IndexModel


class UploadedDocument(Document):
    filename: str
    stored_path: str
    size: int
    source_type: str                    # "pdf", "docx", "txt"
    status: str = "pending"             # pending | processing | ready | failed
    uploaded_by: str                    # user id as string
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:

        name = "documents"
        indexes = [
            IndexModel("uploaded_by"),
            IndexModel("status"),
        ]