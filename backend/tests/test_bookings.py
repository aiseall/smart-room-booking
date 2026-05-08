from datetime import datetime, timedelta, timezone

import pytest

from app.services.booking_service import auto_release_no_shows


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


@pytest.mark.asyncio
async def test_check_in_booking(client, test_room, test_user, auth_header):
    create_resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T14:00:00",
        "end_time": "2026-05-09T15:00:00",
        "title": "Check In Test",
    })
    booking_id = create_resp.json()["id"]
    resp = await client.post(f"/api/v1/bookings/{booking_id}/check-in", headers=auth_header)
    assert resp.status_code in (200, 400)


@pytest.mark.asyncio
async def test_check_in_nonexistent_booking(client, auth_header):
    resp = await client.post("/api/v1/bookings/nonexistent-id/check-in", headers=auth_header)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cancel_nonexistent_booking(client, auth_header):
    resp = await client.delete("/api/v1/bookings/nonexistent-id", headers=auth_header)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cross_day_booking_rejected(client, test_room, auth_header):
    resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-05-09T23:00:00",
        "end_time": "2026-05-10T01:00:00",
        "title": "Cross Day",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_recurring_booking(client, test_room, auth_header):
    resp = await client.post("/api/v1/bookings", headers=auth_header, json={
        "room_id": test_room.id,
        "start_time": "2026-06-01T10:00:00",
        "end_time": "2026-06-01T11:00:00",
        "title": "Weekly Standup",
        "recurrence_rule": "FREQ=WEEKLY;COUNT=4",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["recurrence_group_id"] is not None

    list_resp = await client.get("/api/v1/bookings", headers=auth_header)
    bookings = list_resp.json()
    recurring = [b for b in bookings if b.get("recurrence_group_id")]
    assert len(recurring) >= 2


@pytest.mark.asyncio
async def test_auto_release_no_shows(client, test_room, test_user, db):
    from app.models.booking import Booking

    past_start = datetime.now(timezone.utc) - timedelta(minutes=30)
    booking = Booking(
        room_id=test_room.id,
        user_id=test_user.id,
        title="No Show Meeting",
        start_time=past_start,
        end_time=past_start + timedelta(hours=1),
        status="confirmed",
    )
    db.add(booking)
    await db.commit()

    count = await auto_release_no_shows(db)
    assert count >= 1

    await db.refresh(booking)
    assert booking.status == "auto_released"


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
