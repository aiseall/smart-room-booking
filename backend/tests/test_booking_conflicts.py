import pytest


@pytest.mark.asyncio
async def test_double_booking_returns_409(client, test_room, auth_header):
    resp1 = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:00:00",
        "end_time": "2026-05-09T15:00:00",
        "title": "First Meeting",
    })
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:00:00",
        "end_time": "2026-05-09T15:00:00",
        "title": "Duplicate Meeting",
    })
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_overlapping_start_conflict(client, test_room, auth_header):
    await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:00:00",
        "end_time": "2026-05-09T15:00:00",
        "title": "First",
    })
    resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:30:00",
        "end_time": "2026-05-09T15:30:00",
        "title": "Overlapping",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_adjacent_no_conflict(client, test_room, auth_header):
    await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:00:00",
        "end_time": "2026-05-09T15:00:00",
        "title": "First",
    })
    resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T15:00:00",
        "end_time": "2026-05-09T16:00:00",
        "title": "Adjacent",
    })
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_cancelled_booking_no_conflict(client, test_room, auth_header):
    create_resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:00:00",
        "end_time": "2026-05-09T15:00:00",
        "title": "Will Cancel",
    })
    booking_id = create_resp.json()["id"]
    await client.delete(f"/api/v1/bookings/{booking_id}", headers=auth_header)

    resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:00:00",
        "end_time": "2026-05-09T15:00:00",
        "title": "Rebook",
    })
    assert resp.status_code == 201
