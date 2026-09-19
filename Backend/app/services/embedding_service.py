import asyncio

from google import genai
from google.genai import types

from app.config import settings

_client = genai.Client(api_key=settings.gemini_api_key)

BATCH_SIZE = 50
BATCH_DELAY_SECONDS = 2   # 20 items per 1.5s = ~13 req/min, well under 100
MAX_ATTEMPTS_PER_BATCH = 6   # raise to survive 429s
BASE_BACKOFF_SECONDS = 2   # 2s, 4s, 8s


async def _embed_batch(batch: list[str]) -> list[list[float]]:
    formatted = [types.Content(parts=[types.Part(text=t)]) for t in batch]

    for attempt in range(1, MAX_ATTEMPTS_PER_BATCH + 1):
        try:
            result = await _client.aio.models.embed_content(
                model=settings.embedding_model,
                contents=formatted,
                config=types.EmbedContentConfig(
                    output_dimensionality=settings.embedding_dim
                ),
            )
            return [emb.values for emb in result.embeddings]
        except Exception as e:
            message = str(e)
            is_rate_limit = "429" in message or "RESOURCE_EXHAUSTED" in message

            if attempt == MAX_ATTEMPTS_PER_BATCH:
                raise

            if is_rate_limit:
                wait = 60   # full minute: the quota window resets every 60s
                print(f"Rate limited. Waiting {wait}s before retry {attempt+1}")
            else:
                wait = BASE_BACKOFF_SECONDS ** attempt
                print(f"Embed attempt {attempt} failed: {type(e).__name__}. Retry in {wait}s")

            await asyncio.sleep(wait)

    raise RuntimeError("unreachable")


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    all_vectors: list[list[float]] = []
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        batch_number = i // BATCH_SIZE + 1
        

        try:
            vectors = await _embed_batch(batch)
        except Exception as e:
            print(f"  batch {batch_number} failed permanently: {type(e).__name__}: {e}")
            raise

        if len(vectors) != len(batch):
            raise ValueError(
                f"Batch {batch_number}: expected {len(batch)} vectors, got {len(vectors)}"
            )
        all_vectors.extend(vectors)

        await asyncio.sleep(BATCH_DELAY_SECONDS)

    if len(all_vectors) != len(texts):
        raise ValueError(
            f"Total mismatch: expected {len(texts)} vectors, got {len(all_vectors)}"
        )
    return all_vectors


async def embed_one(text: str) -> list[float]:
    vectors = await embed_texts([text])
    return vectors[0]