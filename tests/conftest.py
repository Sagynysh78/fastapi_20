import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from main import app, get_session
app.router.on_startup.clear()
from settings import settings

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Создаем отдельный движок для тестовой БД
engine_test = create_async_engine(TEST_DATABASE_URL, echo=True)
AsyncSessionTest = sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Создание тестовой БД и таблиц
    import asyncio
    async def create():
        async with engine_test.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    asyncio.run(create())
    yield
    # Очистка после тестов
    async def drop():
        async with engine_test.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
    asyncio.run(drop())

@pytest.fixture()
def client():
    async def override_get_session():
        async with AsyncSessionTest() as session:
            yield session
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c 