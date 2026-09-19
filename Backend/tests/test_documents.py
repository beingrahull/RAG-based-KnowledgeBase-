import io
import uuid

from unittest.mock import AsyncMock, patch


async def _make_user_and_login(client) -> str:
    email = f"doc-{uuid.uuid4().hex[:8]}@example.com"
    await client.post(
        "/api/auth/register",
        json={"name": "DocTest", "email": email, "password": "test1234"},
    )
    r = await client.post(
        "/api/auth/login",
        json={"email": email, "password": "test1234"},
    )
    assert r.status_code == 200
    return email


async def test_upload_requires_auth(client):
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")
    r = await client.post(
        "/api/documents/upload",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
    )
    assert r.status_code == 401


async def test_upload_rejects_unsupported_extension(client):
    await _make_user_and_login(client)
    fake = io.BytesIO(b"plain text")
    r = await client.post(
        "/api/documents/upload",
        files={"file": ("notes.md", fake, "text/markdown")},
    )
    assert r.status_code == 400


async def test_upload_accepts_pdf(client):
    await _make_user_and_login(client)
    fake_pdf = io.BytesIO(b"%PDF-1.4\n%fake test pdf\n")

    with patch("app.routers.documents.run_ingestion", new=AsyncMock()):
        r = await client.post(
            "/api/documents/upload",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        )

    assert r.status_code == 201
    data = r.json()
    assert data["message"] == "File uploaded"
    assert data["document"]["filename"] == "test.pdf"
    assert data["document"]["source_type"] == "pdf"


async def test_list_documents_requires_auth(client):
    r = await client.get("/api/documents")
    assert r.status_code == 401


async def test_list_documents_empty_for_new_user(client):
    await _make_user_and_login(client)
    r = await client.get("/api/documents")
    assert r.status_code == 200
    assert r.json() == []


async def test_list_documents_after_upload(client):
    await _make_user_and_login(client)
    fake_pdf = io.BytesIO(b"%PDF-1.4\n%fake\n")

    with patch("app.routers.documents.run_ingestion", new=AsyncMock()):
        await client.post(
            "/api/documents/upload",
            files={"file": ("list-test.pdf", fake_pdf, "application/pdf")},
        )

    r = await client.get("/api/documents")
    assert r.status_code == 200
    docs = r.json()
    assert len(docs) == 1
    assert docs[0]["filename"] == "list-test.pdf"


async def test_get_document_by_id(client):
    await _make_user_and_login(client)
    fake_pdf = io.BytesIO(b"%PDF-1.4\n%fake\n")

    with patch("app.routers.documents.run_ingestion", new=AsyncMock()):
        upload = await client.post(
            "/api/documents/upload",
            files={"file": ("get-test.pdf", fake_pdf, "application/pdf")},
        )

    doc_id = upload.json()["document"]["id"]

    r = await client.get(f"/api/documents/{doc_id}")
    assert r.status_code == 200
    assert r.json()["id"] == doc_id


async def test_get_nonexistent_document_returns_404(client):
    await _make_user_and_login(client)
    fake_id = "000000000000000000000000"
    r = await client.get(f"/api/documents/{fake_id}")
    assert r.status_code == 404