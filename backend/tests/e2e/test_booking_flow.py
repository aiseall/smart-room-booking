import pytest


@pytest.mark.asyncio
async def test_full_booking_flow(client, test_room, test_user, auth_header):
    # 1. Search available rooms
    search_resp = await client.get(
        "/api/v1/rooms/available?start=2026-05-10T10:00:00&end=2026-05-10T11:00:00",
        headers=auth_header,
    )
    assert search_resp.status_code == 200
    rooms = search_resp.json()
    assert len(rooms) >= 1
    room_id = rooms[0]["id"]

    # 2. Create booking
    book_resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": room_id,
        "start_time": "2026-05-10T10:00:00",
        "end_time": "2026-05-10T11:00:00",
        "title": "E2E Test Meeting",
    })
    assert book_resp.status_code == 201
    booking = book_resp.json()
    assert booking["status"] == "confirmed"
    booking_id = booking["id"]

    # 3. Verify in my bookings
    list_resp = await client.get("/api/v1/bookings", headers=auth_header)
    assert list_resp.status_code == 200
    assert any(b["id"] == booking_id for b in list_resp.json())

    # 4. Conflict detection
    conflict_resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": room_id,
        "start_time": "2026-05-10T10:00:00",
        "end_time": "2026-05-10T11:00:00",
        "title": "Should Fail",
    })
    assert conflict_resp.status_code == 409

    # 5. Room no longer available for that slot
    avail_resp = await client.get(
        "/api/v1/rooms/available?start=2026-05-10T10:00:00&end=2026-05-10T11:00:00",
        headers=auth_header,
    )
    avail_ids = [r["id"] for r in avail_resp.json()]
    assert room_id not in avail_ids

    # 6. Cancel booking
    cancel_resp = await client.delete(f"/api/v1/bookings/{booking_id}", headers=auth_header)
    assert cancel_resp.status_code == 200

    # 7. Room available again after cancellation
    avail_resp2 = await client.get(
        "/api/v1/rooms/available?start=2026-05-10T10:00:00&end=2026-05-10T11:00:00",
        headers=auth_header,
    )
    avail_ids2 = [r["id"] for r in avail_resp2.json()]
    assert room_id in avail_ids2
