import pytest
import pytest

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_register_then_login(client):
    # register
    r = await client.post("/api/auth/register", json={
        "name": "Test",
        "email": "pytest@example.com",
        "password": "test1234",
    })
    assert r.status_code in (201, 401)

    # login
    r = await client.post("/api/auth/login", json={
        "email": "pytest@example.com",
        "password": "test1234",
    })
    assert r.status_code == 200
    assert "Access_Token" in r.cookies