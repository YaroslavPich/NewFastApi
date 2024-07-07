import os
from pathlib import Path

from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import ConnectionConfig



load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DATABASE_URL = os.getenv("DATABASE_URL")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

REDIS_BROKER_URL = os.getenv("REDIS_BROKER_URL")
REDIS_BACKEND_URL = os.getenv("REDIS_BACKEND_URL")
REDIS_URL = os.getenv("REDIS_URL")
REDIS_PORT = os.getenv("REDIS_PORT")

EMAIL_META = os.getenv("EMAIL_META")
PASSWORD_META = os.getenv("PASSWORD_META")

CLOUDINARY_NAME=os.getenv("CLOUDINARY_NAME")
CLOUDINARY_API_KEY=os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_SECRET_KEY=os.getenv("CLOUDINARY_SECRET_KEY")


conf = ConnectionConfig(
    MAIL_USERNAME=EMAIL_META,
    MAIL_PASSWORD=PASSWORD_META,
    MAIL_FROM=EMAIL_META,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.meta.ua",
    MAIL_FROM_NAME="FastAPI",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates'
)

