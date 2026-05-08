from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.rbac import get_current_user
from app.models.user import User
from app.schemas.room import RoomResponse
from app.services.room_service import list_rooms, search_available_rooms

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomResponse])
async def get_rooms(
    building: str | None = None,
    min_capacity: int | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await list_rooms(db, building=building, min_capacity=min_capacity)


@router.get("/available", response_model=list[RoomResponse])
async def get_available_rooms(
    start: datetime = Query(...),
    end: datetime = Query(...),
    min_capacity: int | None = None,
    building: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await search_available_rooms(
        db, start=start, end=end, min_capacity=min_capacity, building=building
    )
