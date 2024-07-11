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

app = FastAPI(title="Contacts API", description='FastAPI application for managing contacts.')

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

async def startup():
    """
    Initialize FastAPILimiter with Redis.
    """
    redis = await aioredis.from_url(f"{REDIS_URL}")
    await FastAPILimiter.init(redis)

@app.on_event("startup")
async def on_startup():
    """
    Startup event to initialize FastAPILimiter.
    """
    await startup()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
