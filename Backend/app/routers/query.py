from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.query import QueryRequest, QueryResponse, SourceRef
from app.services.llm_service import generate_answer
from app.services.prompt_service import build_rag_prompt
from app.services.retrieval_service import retrieve


router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def ask(
    payload: QueryRequest,
    user: User = Depends(get_current_user),
):
    chunks = await retrieve(payload.question)
    

    if not chunks:
        return {
            "answer": "No documents found. Upload a PDF first.",
            "sources": [],
        }

    prompt = build_rag_prompt(payload.question, chunks)

    try:
        result = await generate_answer(prompt)
        
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    sources = [
        SourceRef(
            chunk_number=i,
            document_id=chunks[i - 1]["document_id"],
            text=chunks[i - 1]["text"],
        )
        for i in result.sources
        if 1 <= i <= len(chunks)
    ]

    return {
        "answer": result.answer,
        "sources": sources,
    }