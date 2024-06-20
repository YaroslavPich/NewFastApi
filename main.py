import uvicorn
from fastapi import FastAPI

from src.routes import contacts

app = FastAPI(title="Contacts", description='FastAPI')

app.include_router(contacts.router, prefix="/contacts")


if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
