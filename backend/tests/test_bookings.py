import pytest


@pytest.mark.asyncio
async def test_create_booking(client, test_room, auth_header):
    resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:00:00",
        "end_time": "2026-05-09T15:00:00",
        "title": "Test Meeting",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "confirmed"
    assert data["room_id"] == test_room.id


@pytest.mark.asyncio
async def test_list_my_bookings(client, test_room, auth_header):
    await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:00:00",
        "end_time": "2026-05-09T15:00:00",
        "title": "Test",
    })
    resp = await client.get("/api/v1/bookings", headers=auth_header)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_cancel_booking(client, test_room, auth_header):
    create_resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:00:00",
        "end_time": "2026-05-09T15:00:00",
        "title": "Cancel Me",
    })
    booking_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/bookings/{booking_id}", headers=auth_header)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_validate_end_after_start(client, test_room, auth_header):
    resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T15:00:00",
        "end_time": "2026-05-09T14:00:00",
        "title": "Bad Time",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_validate_30_min_slots(client, test_room, auth_header):
    resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:15:00",
        "end_time": "2026-05-09T15:00:00",
        "title": "Bad Slot",
    })
    assert resp.status_code == 422
