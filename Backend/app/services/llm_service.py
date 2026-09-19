import json

from google import genai
from pydantic import ValidationError

from app.config import settings
from app.schemas.llm_output import LLMAnswer


_client = genai.Client(api_key=settings.gemini_api_key)



async def generate_answer(prompt: str) -> LLMAnswer:
    """
    Call Gemini with the RAG prompt. Parse the response as JSON
    and validate it against the LLMAnswer schema.
    """
    response = await _client.aio.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )

    raw = response.text

    try:
        data = json.loads(raw)
        return LLMAnswer(**data)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {raw[:200]}") from e
    except ValidationError as e:
        raise ValueError(f"LLM JSON does not match schema: {e}") from e