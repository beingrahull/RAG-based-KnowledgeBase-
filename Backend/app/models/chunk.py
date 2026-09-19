from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel


class Chunk(Document):
    document_id: PydanticObjectId
    chunk_index: int
    text: str
    embedding: list[float]
    page_number: int | None = None
    section_heading: str | None = None

    class Settings:
        name = "chunks"
        indexes = [
            IndexModel("document_id"),
        ]