from datetime import datetime

from pydantic import BaseModel

   
class DocumentPublic(BaseModel):
    id: str
    filename: str
    size: int
    source_type: str
    status: str
    uploaded_at: datetime


class UploadResponse(BaseModel):
    message: str
    document: DocumentPublic