import json
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.rbac import require_role
from app.models.user import User
from app.schemas.room import RoomCreate, RoomResponse
from app.services.room_service import create_room, get_utilization

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/rooms", response_model=RoomResponse, status_code=201)
async def add_room(
    body: RoomCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("facility_admin")),
):
    return await create_room(db, body)


@router.get("/utilization")
async def utilization(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    building: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("facility_admin")),
):
    return await get_utilization(db, start_date=start_date, end_date=end_date, building=building)
