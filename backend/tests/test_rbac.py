import pytest


@pytest.mark.asyncio
async def test_admin_endpoint_forbidden_for_employee(client, test_user, auth_header):
    resp = await client.get("/api/v1/admin/utilization", headers=auth_header)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_endpoint_allowed_for_admin(client, admin_user, admin_header):
    resp = await client.get("/api/v1/admin/utilization", headers=admin_header)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_room_forbidden_for_employee(client, test_user, auth_header):
    resp = await client.post("/api/v1/admin/rooms", headers=auth_header, json={
        "name": "X-101", "building": "A", "floor": 1, "capacity": 5,
    })
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_room_allowed_for_admin(client, admin_user, admin_header):
    resp = await client.post("/api/v1/admin/rooms", headers=admin_header, json={
        "name": "X-101", "building": "A", "floor": 1, "capacity": 5, "equipment": ["whiteboard"],
    })
    assert resp.status_code == 201
