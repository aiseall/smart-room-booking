import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.booking import Booking, CheckIn
from app.schemas.booking import BookingCreate


async def create_booking(db: AsyncSession, user_id: str, data: BookingCreate) -> Booking:
    if data.start_time.date() != data.end_time.date():
        raise HTTPException(status_code=400, detail="Bookings must start and end on the same day")

    conflict = await _check_conflict(db, data.room_id, data.start_time, data.end_time)
    if conflict:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room already booked for this time slot")

    if data.recurrence_rule:
        return await _create_recurring(db, user_id, data)

    booking = Booking(
        room_id=data.room_id,
        user_id=user_id,
        title=data.title,
        start_time=data.start_time,
        end_time=data.end_time,
        status="confirmed",
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


async def _check_conflict(
    db: AsyncSession, room_id: str, start: datetime, end: datetime, exclude_id: str | None = None
) -> bool:
    query = select(Booking).where(
        Booking.room_id == room_id,
        Booking.status.not_in(["cancelled", "auto_released"]),
        Booking.start_time < end,
        Booking.end_time > start,
    )
    if exclude_id:
        query = query.where(Booking.id != exclude_id)
    result = await db.execute(query)
    return result.first() is not None


async def _create_recurring(db: AsyncSession, user_id: str, data: BookingCreate) -> Booking:
    group_id = str(uuid.uuid4())
    first_booking = None

    current_start = data.start_time
    current_end = data.end_time
    duration = data.end_time - data.start_time
    created_count = 0
    skipped_count = 0

    for _ in range(52):
        conflict = await _check_conflict(db, data.room_id, current_start, current_end)
        if not conflict:
            booking = Booking(
                room_id=data.room_id,
                user_id=user_id,
                title=data.title,
                start_time=current_start,
                end_time=current_end,
                status="confirmed",
                recurrence_rule=data.recurrence_rule,
                recurrence_group_id=group_id,
            )
            db.add(booking)
            if first_booking is None:
                first_booking = booking
            created_count += 1
        else:
            skipped_count += 1

        current_start += timedelta(weeks=1)
        current_end = current_start + duration

        if created_count + skipped_count >= 4:
            break

    await db.commit()
    if first_booking:
        await db.refresh(first_booking)
    return first_booking


async def list_user_bookings(db: AsyncSession, user_id: str) -> list[Booking]:
    result = await db.execute(
        select(Booking)
        .where(Booking.user_id == user_id)
        .order_by(Booking.start_time.desc())
    )
    return list(result.scalars().all())


async def get_booking_by_id(db: AsyncSession, booking_id: str) -> Booking | None:
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    return result.scalar_one_or_none()


async def cancel_booking(db: AsyncSession, booking: Booking) -> None:
    booking.status = "cancelled"
    booking.updated_at = datetime.now(timezone.utc)
    await db.commit()


async def check_in_booking(db: AsyncSession, booking: Booking) -> None:
    if booking.status != "confirmed":
        raise HTTPException(status_code=400, detail=f"Cannot check in: booking status is '{booking.status}'")
    now = datetime.now(timezone.utc)
    if now < booking.start_time - timedelta(minutes=10):
        raise HTTPException(status_code=400, detail="Too early to check in (max 10 minutes before start)")

    booking.status = "checked_in"
    booking.updated_at = now
    check_in = CheckIn(booking_id=booking.id, checked_in_at=now)
    db.add(check_in)
    await db.commit()


async def auto_release_no_shows(db: AsyncSession) -> int:
    now = datetime.now(timezone.utc)
    grace_cutoff = now - timedelta(minutes=settings.AUTO_RELEASE_MINUTES)

    result = await db.execute(
        select(Booking).where(
            Booking.status == "confirmed",
            Booking.start_time <= grace_cutoff,
        )
    )
    bookings = result.scalars().all()
    count = 0
    for booking in bookings:
        booking.status = "auto_released"
        booking.updated_at = now
        count += 1
    if count > 0:
        await db.commit()
    return count
