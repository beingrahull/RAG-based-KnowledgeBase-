import uuid
from unittest.mock import AsyncMock, patch
import pytest

pytestmark = pytest.mark.asyncio

from app.schemas.llm_output import LLMAnswer


async def _make_user_and_login(client) -> dict:
    email = f"q-{uuid.uuid4().hex[:8]}@example.com"
    await client.post(
        "/api/auth/register",
        json={"name": "QTest", "email": email, "password": "test1234"},
    )
    r = await client.post(
        "/api/auth/login",
        json={"email": email, "password": "test1234"},
    )
    return {"Access_Token": r.cookies.get("Access_Token")}


async def test_query_requires_auth(client):
    r = await client.post("/api/query", json={"question": "What is ARP?"})
    assert r.status_code == 401


async def test_query_rejects_empty_question(client):
    cookies = await _make_user_and_login(client)
    r = await client.post(
        "/api/query",
        json={"question": ""},
        cookies=cookies,
    )
    assert r.status_code == 422


async def test_query_returns_answer_with_mocked_llm(client):
    cookies = await _make_user_and_login(client)

    fake_chunks = [
        {
            "id": "doc1#chunk0",
            "score": 0.9,
            "text": "ARP maps an IP address to a MAC address.",
            "document_id": "doc1",
        }
    ]

    with patch(
        "app.routers.query.retrieve",
        new=AsyncMock(return_value=fake_chunks),
    ), patch(
        "app.routers.query.generate_answer",
        new=AsyncMock(return_value=LLMAnswer(answer="ARP maps IP to MAC.", sources=[1])),
    ):
        r = await client.post(
            "/api/query",
            json={"question": "What is ARP?"},
            cookies=cookies,
        )

    assert r.status_code == 200
    data = r.json()
    assert data["answer"] == "ARP maps IP to MAC."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["chunk_number"] == 1


async def test_query_returns_graceful_message_when_no_chunks(client):
    cookies = await _make_user_and_login(client)

    with patch(
        "app.routers.query.retrieve",
        new=AsyncMock(return_value=[]),
    ):
        r = await client.post(
            "/api/query",
            json={"question": "Anything?"},
            cookies=cookies,
        )

    assert r.status_code == 200
    data = r.json()
    assert data["sources"] == []
    assert "No documents" in data["answer"] or "I don't know" in data["answer"]