import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.db import engine
from app.models import Base
from app.services.booking_service import auto_release_no_shows
from app.core.db import async_session
from app.models.user import User

logger = logging.getLogger(__name__)


async def _auto_release_loop():
    while True:
        try:
            async with async_session() as db:
                count = await auto_release_no_shows(db)
                if count > 0:
                    logger.info(f"Auto-released {count} no-show booking(s)")
        except Exception as e:
            logger.error(f"Auto-release error: {e}")
        await asyncio.sleep(settings.AUTO_RELEASE_CHECK_INTERVAL)


async def _seed_if_empty():
    from sqlalchemy import select, func
    async with async_session() as db:
        result = await db.execute(select(func.count()).select_from(User))
        if result.scalar() == 0:
            logger.info("Empty database detected, running seed...")
            from app.scripts.seed import seed
            await seed()
            logger.info("Seed complete.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _seed_if_empty()
    task = asyncio.create_task(_auto_release_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Smart Room Booking API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

try:
    import os
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    if os.path.isdir(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
except Exception:
    pass
