import pytest


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    resp = await client.post("/api/v1/auth/login", json={"username": "testuser", "password": "test123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    resp = await client.post("/api/v1/auth/login", json={"username": "testuser", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    resp = await client.post("/api/v1/auth/login", json={"username": "noone", "password": "pass"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client, test_user, auth_header):
    resp = await client.get("/api/v1/auth/me", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_me_no_token(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)
