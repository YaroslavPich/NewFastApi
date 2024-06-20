import uvicorn
from fastapi import FastAPI

from src.routes import contacts
from src.database.database import engine

app = FastAPI(title="Contacts", description='FastAPI')

app.include_router(contacts.router, prefix="/contacts")


@app.get("/")
def read_root():
	return {"message": "Welcome to FastAPI"}


if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
