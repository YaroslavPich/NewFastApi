import uvicorn
from fastapi import FastAPI

from src.routes import contacts, users

app = FastAPI(title="Contacts", description='FastAPI')

app.include_router(contacts.router)
app.include_router(users.router)

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
