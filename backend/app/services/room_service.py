import json
from datetime import date, datetime, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.room import Room
from app.schemas.room import RoomCreate


async def list_rooms(
    db: AsyncSession,
    building: str | None = None,
    min_capacity: int | None = None,
) -> list[Room]:
    query = select(Room).where(Room.is_active == True)
    if building:
        query = query.where(Room.building == building)
    if min_capacity:
        query = query.where(Room.capacity >= min_capacity)
    query = query.order_by(Room.building, Room.name)
    result = await db.execute(query)
    return list(result.scalars().all())


async def search_available_rooms(
    db: AsyncSession,
    start: datetime,
    end: datetime,
    min_capacity: int | None = None,
    building: str | None = None,
) -> list[Room]:
    booked_room_ids = (
        select(Booking.room_id)
        .where(
            Booking.status.not_in(["cancelled", "auto_released"]),
            Booking.start_time < end,
            Booking.end_time > start,
        )
        .scalar_subquery()
    )

    query = select(Room).where(Room.is_active == True, Room.id.not_in(booked_room_ids))
    if building:
        query = query.where(Room.building == building)
    if min_capacity:
        query = query.where(Room.capacity >= min_capacity)
    query = query.order_by(Room.building, Room.name)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_room(db: AsyncSession, data: RoomCreate) -> Room:
    room = Room(
        name=data.name,
        building=data.building,
        floor=data.floor,
        capacity=data.capacity,
        equipment=json.dumps(data.equipment),
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


async def get_utilization(
    db: AsyncSession,
    start_date: date | None = None,
    end_date: date | None = None,
    building: str | None = None,
) -> dict:
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    rooms_query = select(Room).where(Room.is_active == True)
    if building:
        rooms_query = rooms_query.where(Room.building == building)
    rooms_result = await db.execute(rooms_query)
    rooms = rooms_result.scalars().all()

    room_stats = []
    for room in rooms:
        bookings_query = select(Booking).where(
            Booking.room_id == room.id,
            Booking.start_time >= start_dt,
            Booking.end_time <= end_dt,
        )
        bookings_result = await db.execute(bookings_query)
        bookings = bookings_result.scalars().all()

        total = len(bookings)
        no_shows = sum(1 for b in bookings if b.status in ("no_show", "auto_released"))
        checked_in = sum(1 for b in bookings if b.status in ("checked_in", "completed"))
        total_hours = sum(
            (b.end_time - b.start_time).total_seconds() / 3600 for b in bookings
        )
        days = max((end_date - start_date).days, 1)
        available_hours = days * 10
        utilization_pct = round((total_hours / available_hours) * 100, 1) if available_hours else 0

        room_stats.append({
            "room_id": room.id,
            "room_name": room.name,
            "building": room.building,
            "total_bookings": total,
            "no_show_count": no_shows,
            "checked_in_count": checked_in,
            "total_hours": round(total_hours, 1),
            "utilization_percent": utilization_pct,
        })

    by_building = {}
    for stat in room_stats:
        b = stat["building"]
        if b not in by_building:
            by_building[b] = {"total_bookings": 0, "no_show_count": 0, "total_hours": 0}
        by_building[b]["total_bookings"] += stat["total_bookings"]
        by_building[b]["no_show_count"] += stat["no_show_count"]
        by_building[b]["total_hours"] += stat["total_hours"]

    return {
        "period": {"start": str(start_date), "end": str(end_date)},
        "rooms": room_stats,
        "by_building": by_building,
        "summary": {
            "total_rooms": len(rooms),
            "total_bookings": sum(s["total_bookings"] for s in room_stats),
            "total_no_shows": sum(s["no_show_count"] for s in room_stats),
        },
    }
