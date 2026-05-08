import asyncio
import json

from app.core.db import engine, async_session
from app.models import Base
from app.models.user import User
from app.models.room import Room
from app.services.auth_service import hash_password


USERS = [
    {"username": "alice", "email": "alice@company.com", "name": "Alice Wang", "password": "pass123", "role": "employee", "department": "Engineering"},
    {"username": "bob", "email": "bob@company.com", "name": "Bob Li", "password": "pass123", "role": "employee", "department": "Marketing"},
    {"username": "charlie", "email": "charlie@company.com", "name": "Charlie Chen", "password": "pass123", "role": "team_admin", "department": "Engineering"},
    {"username": "diana", "email": "diana@company.com", "name": "Diana Zhang", "password": "pass123", "role": "facility_admin", "department": "Operations"},
    {"username": "admin", "email": "admin@company.com", "name": "Admin User", "password": "admin123", "role": "facility_admin", "department": "IT"},
]

BUILDINGS = {
    "A": {"floors": 3, "rooms_per_floor": 4},
    "B": {"floors": 3, "rooms_per_floor": 3},
    "C": {"floors": 2, "rooms_per_floor": 3},
}

ROOM_CONFIGS = [
    {"capacity": 4, "equipment": ["whiteboard"]},
    {"capacity": 8, "equipment": ["whiteboard", "projector"]},
    {"capacity": 12, "equipment": ["whiteboard", "projector", "video_conf"]},
    {"capacity": 20, "equipment": ["whiteboard", "projector", "video_conf", "sound_system"]},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        for u in USERS:
            user = User(
                username=u["username"],
                email=u["email"],
                name=u["name"],
                password_hash=hash_password(u["password"]),
                role=u["role"],
                department=u["department"],
            )
            db.add(user)

        room_idx = 0
        for building, config in BUILDINGS.items():
            for floor in range(1, config["floors"] + 1):
                for i in range(1, config["rooms_per_floor"] + 1):
                    rc = ROOM_CONFIGS[room_idx % len(ROOM_CONFIGS)]
                    room = Room(
                        name=f"{building}-{floor}0{i}",
                        building=building,
                        floor=floor,
                        capacity=rc["capacity"],
                        equipment=json.dumps(rc["equipment"]),
                    )
                    db.add(room)
                    room_idx += 1

        await db.commit()

    print(f"Seeded {len(USERS)} users and {room_idx} rooms.")


if __name__ == "__main__":
    asyncio.run(seed())
