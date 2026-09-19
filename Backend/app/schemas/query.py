from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class SourceRef(BaseModel):
    chunk_number: int
    document_id: str
    text: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceRef]