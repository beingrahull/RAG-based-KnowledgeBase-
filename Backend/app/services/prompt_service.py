def build_rag_prompt(question: str, chunks: list[dict]) -> str:
    if not chunks:
        context = "(no context available)"
    else:
        context = "\n\n".join(
            f"[{i}] (document: {c['document_id']}):\n{c['text']}"
            for i, c in enumerate(chunks, start=1)
        )

    prompt = f"""You are a helpful assistant. Answer the user's question using ONLY the context below.

Rules:
- Answer using ONLY the information in the context below.
- If the context contains information that answers the question, use it, even if the wording differs.
- Only if the context is completely unrelated to the question, respond with:
  {{"answer": "I don't know based on the provided documents.", "sources": []}}
- Return ONLY valid JSON in this exact shape:
  {{"answer": "<your answer>", "sources": [<chunk numbers you used>]}}

CONTEXT:
{context}

QUESTION:
{question}
"""

    
    return prompt