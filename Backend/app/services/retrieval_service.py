from app.config import settings
from app.services.embedding_service import embed_one
from app.services.vector_store_service import query_chunks


async def retrieve(question: str, top_k: int | None = None) -> list[dict]:
    if not question.strip():
        return []

    k = top_k if top_k is not None else settings.top_k_retrieve
    query_embedding = await embed_one(question)
    return query_chunks(query_embedding, top_k=k)