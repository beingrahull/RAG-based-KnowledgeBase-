def chunk_contains_all_keywords(chunk_text: str, keywords: list[str]) -> bool:
    """True if every keyword appears in the chunk, case-insensitive."""
    text = chunk_text.lower()
    return all(kw.lower() in text for kw in keywords)


def is_hit(retrieved_chunks: list[dict], keywords: list[str]) -> bool:
    """True if at least one retrieved chunk contains all keywords."""
    return any(
        chunk_contains_all_keywords(c.get("text", ""), keywords)
        for c in retrieved_chunks
    )