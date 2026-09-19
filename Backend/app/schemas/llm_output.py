from pydantic import BaseModel


class LLMAnswer(BaseModel):
    answer: str
    sources: list[int]