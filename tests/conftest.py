import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from main import app
from core.database import get_db, Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_test = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    async with async_session_test() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def master_data():
    return {"name": "Тест Мастер", "phone": "+79991234567", "password": "testpass123"}


@pytest_asyncio.fixture
async def registered_master(client, master_data):
    res = await client.post("/auth/register", json=master_data)
    assert res.status_code == 200
    return res.json()


@pytest_asyncio.fixture
async def auth_headers(client, master_data, registered_master):
    res = await client.post(
        "/auth/login",
        json={"phone": master_data["phone"], "password": master_data["password"]},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def master_with_service(client, auth_headers):
    res = await client.post(
        "/services/",
        json={"name": "Маникюр", "duration": 60, "price": 1500},
        headers=auth_headers,
    )
    return res.json()


@pytest_asyncio.fixture
async def master_with_schedule(client, auth_headers):
    await client.put(
        "/schedule/0",
        json={"start_time": "09:00", "end_time": "18:00", "is_working": True},
        headers=auth_headers,
    )
