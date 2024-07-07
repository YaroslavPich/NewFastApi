import aioredis
import uvicorn
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from src.settings import REDIS_URL
from fastapi.middleware.cors import CORSMiddleware

from src.routes import contacts, users, auth

origin = [
    "*"
]

app = FastAPI(title="Contacts", description='FastAPI')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

app.include_router(contacts.router)
app.include_router(users.router)
app.include_router(auth.router)


async def startup():
    redis = await aioredis.from_url(f"{REDIS_URL}")
    await FastAPILimiter.init(redis)


@app.on_event("startup")
async def on_startup():
    await startup()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
