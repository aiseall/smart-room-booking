from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.rbac import get_current_user
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import (
    cancel_booking,
    check_in_booking,
    create_booking,
    get_booking_by_id,
    list_user_bookings,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingResponse])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    bookings = await list_user_bookings(db, user.id)
    return [_to_response(b) for b in bookings]


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_new_booking(
    body: BookingCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = await create_booking(db, user.id, body)
    return _to_response(booking)


@router.delete("/{booking_id}")
async def cancel_my_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = await get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id and user.role == "employee":
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
    await cancel_booking(db, booking)
    return {"detail": "Booking cancelled"}


@router.post("/{booking_id}/check-in")
async def check_in(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = await get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your booking")
    await check_in_booking(db, booking)
    return {"detail": "Checked in successfully"}


def _to_response(booking) -> BookingResponse:
    return BookingResponse(
        id=booking.id,
        room_id=booking.room_id,
        user_id=booking.user_id,
        title=booking.title,
        start_time=booking.start_time,
        end_time=booking.end_time,
        status=booking.status,
        recurrence_rule=booking.recurrence_rule,
        recurrence_group_id=booking.recurrence_group_id,
        created_at=booking.created_at,
        room=booking.room if booking.room else None,
        checked_in=booking.check_in is not None,
    )
