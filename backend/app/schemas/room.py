import json
from datetime import datetime

from pydantic import BaseModel, field_validator


class RoomResponse(BaseModel):
    id: str
    name: str
    building: str
    floor: int
    capacity: int
    equipment: list[str]
    is_active: bool

    model_config = {"from_attributes": True}

    @field_validator("equipment", mode="before")
    @classmethod
    def parse_equipment(cls, v):
        if isinstance(v, str):
            return json.loads(v) if v else []
        return v or []


class RoomCreate(BaseModel):
    name: str
    building: str
    floor: int
    capacity: int
    equipment: list[str] = []


class RoomSearchQuery(BaseModel):
    start: datetime
    end: datetime
    min_capacity: int | None = None
    building: str | None = None
