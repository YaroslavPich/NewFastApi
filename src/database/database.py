from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio_redis
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
    redis = await asyncio_redis.Connection.create(
        host=REDIS_URL.hostname,
        port=REDIS_URL.port,
    )
    try:
        yield redis
    finally:
        await redis.close()
