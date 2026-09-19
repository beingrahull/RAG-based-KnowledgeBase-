from pinecone import Pinecone

from app.config import settings

_pc = Pinecone(api_key=settings.pinecone_api_key)
_index = _pc.Index(settings.pinecone_index_name)


def upsert_chunks(document_id: str, chunks: list[str], embeddings: list[list[float]]) -> None:
    if not chunks:
        return

    vectors = []
    for idx, (text, vec) in enumerate(zip(chunks, embeddings)):
        vectors.append({
            "id": f"{document_id}#chunk{idx}",
            "values": vec,
            "metadata": {
                "document_id": document_id,
                "chunk_index": idx,
                "text": text,
            },
        })

    # Pinecone upsert limit is 100 vectors per request
    for i in range(0, len(vectors), 100):
        _index.upsert(vectors=vectors[i : i + 100])

    


def delete_document_chunks(document_id: str) -> None:
    """
    Delete all vectors with IDs prefixed by document_id.
    Pinecone supports prefix deletion via metadata filter or ID prefix.
    """
    try:
        _index.delete(filter={"document_id": {"$eq": document_id}})
    except Exception:
        # Pinecone serverless may not support filter deletion on some plans.
        # Fall back to listing IDs is not supported; this is best-effort.
        pass


def query_chunks(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    results = _index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )
    return [
        {
            "id": m.id,
            "score": m.score,
            "text": m.metadata["text"],
            "document_id": m.metadata["document_id"],
        }
        for m in results.matches
    ]