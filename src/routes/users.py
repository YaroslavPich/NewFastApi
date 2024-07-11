from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Security, BackgroundTasks

from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from src.schemas import UserModel
from celery_worker import send_test_email_task
from src.database.database import get_db
from src.repository.users import UserService, UsernameTaken, LoginFailed
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/users", tags=["users"])

user_service = UserService()

security = HTTPBearer()


@router.post(
    "/signup", response_class=JSONResponse, status_code=status.HTTP_201_CREATED
)
async def signup(body: UserModel, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    :param body: The user registration details.
    :type body: UserModel
    :param db: The database session.
    :type db: AsyncSession
    :return: The username and email of the newly created user.
    :rtype: dict
    :raises HTTPException: If the username or email already exists.
    """
    try:
        new_user = await user_service.create_new_user(body, db)
    except UsernameTaken:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User or email already exist"
        )
    user_data = {"new_user": new_user.username, "Email": new_user.email}
    return user_data


@router.post("/login")
async def login(
        body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Authenticate a user and return access and refresh tokens.

    :param body: The login details.
    :type body: OAuth2PasswordRequestForm
    :param db: The database session.
    :type db: AsyncSession
    :return: The access token, refresh token, and token type.
    :rtype: dict
    :raises HTTPException: If the login credentials are invalid.
    """
    try:
        access_token, refresh_token = await user_service.login_user(body, db)
    except LoginFailed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Invalid credentials"
        )
    user_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
    return user_data


@router.post(
    "/refresh_token", response_class=JSONResponse, status_code=status.HTTP_201_CREATED
)
async def refresh_token(
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: AsyncSession = Depends(get_db),
):
    """
    Refresh an access token using a refresh token.

    :param credentials: The refresh token credentials.
    :type credentials: HTTPAuthorizationCredentials
    :param db: The database session.
    :type db: AsyncSession
    :return: The new access token, refresh token, and token type.
    :rtype: dict
    """
    token = credentials.credentials
    access_token = await user_service.refresh_token(token, db)
    return {
        "access_token": access_token,
        "refresh_token": token,
        "token_type": "bearer",
    }


@router.post('/send_test_email')
async def send_test_email(email_to_send: str, background_task: BackgroundTasks):
    """
    Send a tests email asynchronously.

    :param email_to_send: The email address to send the tests email to.
    :type email_to_send: str
    :param background_task: The background task instance.
    :type background_task: BackgroundTasks
    """
    send_test_email_task.delay(email_to_send)
