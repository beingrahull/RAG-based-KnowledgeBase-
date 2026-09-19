from app.models.document import UploadedDocument
from app.services.chunking_service import chunk_text
from app.services.embedding_service import embed_texts
from app.services.vector_store_service import delete_document_chunks, upsert_chunks
from app.utils.pdf_parser import extract_text_from_pdf


async def run_ingestion(document_id: str) -> None:
    doc = await UploadedDocument.get(document_id)
    if not doc:
        print(f"[{document_id}] not found")
        return

    try:
        doc.status = "processing"
        await doc.save()
        

        # 0. Clear any previous chunks for this document (safe on retry)
        delete_document_chunks(str(doc.id))

        # 1. Extract text
        text = extract_text_from_pdf(doc.stored_path)
        if not text.strip():
            raise ValueError("Extracted text is empty. PDF may be a scan.")
        

        # 2. Chunk
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("Chunking produced zero chunks.")
        

        # 3. Embed (batched, retried)
        embeddings = await embed_texts(chunks)
        if len(embeddings) != len(chunks):
            raise ValueError(
                f"Embedding count mismatch: {len(embeddings)} vs {len(chunks)}"
            )
        

        # 4. Upsert to Pinecone
        upsert_chunks(str(doc.id), chunks, embeddings)

        # 5. Mark ready
        doc.status = "ready"
        await doc.save()
        

    except Exception as e:
        print(f"[{document_id}] FAILED: {type(e).__name__}: {e}")
        doc.status = "failed"
        await doc.save()
        # do NOT re-raise — the response was already sent