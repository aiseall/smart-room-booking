from datetime import datetime

from pydantic import BaseModel, field_validator


class BookingCreate(BaseModel):
    room_id: str
    start_time: datetime
    end_time: datetime
    title: str
    recurrence_rule: str | None = None

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v, info):
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_30_min_slots(cls, v):
        if v.minute % 30 != 0:
            raise ValueError("Time must be on 30-minute boundaries (e.g. :00 or :30)")
        if v.second != 0 or v.microsecond != 0:
            raise ValueError("Seconds and microseconds must be zero")
        return v


class BookingResponse(BaseModel):
    id: str
    room_id: str
    user_id: str
    title: str
    start_time: datetime
    end_time: datetime
    status: str
    recurrence_rule: str | None = None
    recurrence_group_id: str | None = None
    created_at: datetime
    room: "RoomInBooking | None" = None
    checked_in: bool = False

    model_config = {"from_attributes": True}


class RoomInBooking(BaseModel):
    id: str
    name: str
    building: str
    floor: int
    capacity: int

    model_config = {"from_attributes": True}
