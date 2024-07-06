from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aioredis
from src.settings import DATABASE_URL, REDIS_URL

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


async def get_db():
    async with SessionLocal() as session:
        yield session


async def get_redis_client():
    redis = aioredis.from_url(REDIS_URL)
    try:
        yield redis
    finally:
        await redis.close()
