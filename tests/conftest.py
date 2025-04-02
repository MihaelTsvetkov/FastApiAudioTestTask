import config
from config import Settings

_test_settings = Settings(
    _env_file=None,
    POSTGRES_HOST="localhost",
    POSTGRES_PORT=5433,
    POSTGRES_USER="test_user",
    POSTGRES_PASSWORD="test_password",
    POSTGRES_DB="test_db",
    JWT_SECRET_KEY="TEST_SUPERSECRET",
    JWT_ALGORITHM="HS256",
)
config.get_settings.cache_clear()
config.get_settings = lambda: _test_settings

import pytest
import pytest_asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Any

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy import delete
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport

from main import create_app
from database import Base
from models.user import User
from services.auth_service import create_access_token


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return config.get_settings()


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_settings: Settings) -> AsyncGenerator[AsyncEngine, Any]:
    engine = create_async_engine(test_settings.DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database(test_engine: AsyncEngine) -> AsyncGenerator[None, Any]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[Any, Any]:
    SessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession)
    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(
    test_settings: Settings,
    db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, Any]:
    test_app = create_app(test_settings)

    with patch("database.get_session") as mock_get_session:
        async def override_get_session() -> AsyncGenerator[AsyncSession, Any]:
            yield db_session

        mock_get_session.side_effect = override_get_session

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest_asyncio.fixture(autouse=True)
async def cleanup_users(db_session: AsyncSession) -> AsyncGenerator[None, Any]:
    await db_session.execute(delete(User))
    await db_session.commit()
    yield


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> AsyncGenerator[User, Any]:
    user = User(
        yandex_id="some_yandex_id",
        email="test_user@example.com",
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user


@pytest_asyncio.fixture
async def superuser(db_session: AsyncSession) -> AsyncGenerator[User, Any]:
    user = User(
        yandex_id="admin_yandex_id",
        email="admin@example.com",
        is_superuser=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user


@pytest_asyncio.fixture
async def user_token(
    test_user: User,
    test_settings: Settings
) -> str:
    return create_access_token(test_user.id, settings=test_settings)


@pytest_asyncio.fixture
async def superuser_token(
    superuser: User,
    test_settings: Settings
) -> str:
    return create_access_token(superuser.id, settings=test_settings)


@pytest_asyncio.fixture
async def uploaded_file(
    client: AsyncClient,
    user_token: str
) -> AsyncGenerator[str, Any]:
    headers = {"Authorization": f"Bearer {user_token}"}
    temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    temp_path = Path(temp_file.name)
    temp_file.write(b"Fake MP3 content")
    temp_file.close()

    try:
        with open(temp_path, "rb") as f:
            response = await client.post(
                "/files/upload",
                headers=headers,
                files={
                    "filename": (None, temp_path.name),
                    "file": (temp_path.name, f, "audio/mpeg")
                },
            )
            assert response.status_code == 201
            yield temp_path.name
    finally:
        temp_path.unlink(missing_ok=True)
