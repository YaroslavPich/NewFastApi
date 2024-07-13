import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from main import app
from src.database.models import Base
from src.database.database import get_db

# Define a test database URL
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# SQLAlchemy engine and session setup
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="module")
async def session():
    await init_models()
    async with SessionLocal() as local_session:
        yield local_session


@pytest_asyncio.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {"username": "deadpool", "email": "deadpool@example.com", "password": "123456789"}