import pytest


@pytest.mark.asyncio
async def test_list_rooms(client, test_room, auth_header):
    resp = await client.get("/api/v1/rooms", headers=auth_header)
    assert resp.status_code == 200
    rooms = resp.json()
    assert len(rooms) >= 1
    assert rooms[0]["name"] == "A-101"


@pytest.mark.asyncio
async def test_list_rooms_filter_building(client, test_room, auth_header):
    resp = await client.get("/api/v1/rooms?building=B", headers=auth_header)
    assert resp.status_code == 200
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_search_available(client, test_room, auth_header):
    resp = await client.get(
        "/api/v1/rooms/available?start=2026-05-09T14:00:00&end=2026-05-09T15:00:00",
        headers=auth_header,
    )
    assert resp.status_code == 200
    rooms = resp.json()
    assert len(rooms) >= 1


@pytest.mark.asyncio
async def test_rooms_require_auth(client, test_room):
    resp = await client.get("/api/v1/rooms")
    assert resp.status_code == 403
