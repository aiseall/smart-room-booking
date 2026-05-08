import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.db import get_db
from app.main import app
from app.models import Base
from app.models.user import User
from app.models.room import Room
from app.services.auth_service import hash_password, create_access_token

test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestSession() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def db():
    async with TestSession() as session:
        yield session


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(db: AsyncSession):
    user = User(
        username="testuser", email="test@test.com", name="Test User",
        password_hash=hash_password("test123"), role="employee", department="Test",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def admin_user(db: AsyncSession):
    user = User(
        username="admin", email="admin@test.com", name="Admin",
        password_hash=hash_password("admin123"), role="facility_admin", department="Ops",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_room(db: AsyncSession):
    room = Room(name="A-101", building="A", floor=1, capacity=10, equipment='["projector"]')
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


@pytest.fixture
async def auth_header(test_user):
    token = create_access_token(test_user.id, test_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_header(admin_user):
    token = create_access_token(admin_user.id, admin_user.role)
    return {"Authorization": f"Bearer {token}"}
