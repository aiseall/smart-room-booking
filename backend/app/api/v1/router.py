from fastapi import APIRouter

from app.api.v1 import admin, auth, bookings, health, rooms

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(rooms.router)
api_router.include_router(bookings.router)
api_router.include_router(admin.router)
