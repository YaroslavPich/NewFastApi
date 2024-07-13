from fastapi import APIRouter, Depends, HTTPException, status, Security, Request
from src.schemas import RequestEmail
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from src.database.database import get_db
from src.repository.users import UserService
from src.repository.auth import get_email_from_token, create_email_token, Hash
from celery_worker import send_email

router = APIRouter()

security = HTTPBearer()

user_service = UserService()

hash_handler = Hash()

@router.post(
    "/refresh_token", response_class=JSONResponse, status_code=status.HTTP_201_CREATED
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Refreshes an access token using a refresh token.

    :param credentials: HTTP Authorization credentials containing the refresh token.
    :type credentials: HTTPAuthorizationCredentials
    :param db: The async database session.
    :type db: AsyncSession
    :return: Dictionary containing new access token, refresh token, and token type.
    :rtype: dict
    """
    token = credentials.credentials
    access_token = await user_service.refresh_token(token, db)
    return {
        "access_token": access_token,
        "refresh_token": token,
        "token_type": "bearer",
    }


@router.post('/request_email')
async def request_email(
    body: RequestEmail,
    request: Request,
    db: AsyncSession = Depends(get_db)):
    """
    Sends an email confirmation request to the user.

    :param body: Request body containing email address.
    :type body: RequestEmail
    :param request: The FastAPI Request object.
    :type request: Request
    :param db: The async database session.
    :type db: AsyncSession
    :return: Message indicating the result of the email request.
    :rtype: dict
    """
    user = await UserService.get_user_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await send_email(user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirms user's email using the provided confirmation token.

    :param token: Confirmation token sent to the user.
    :type token: str
    :param db: The async database session.
    :type db: AsyncSession
    :return: Message indicating the result of the email confirmation.
    :rtype: dict
    """
    email = await get_email_from_token(token)
    user = await UserService.get_user_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await UserService.confirmed_email(email, db)
    return {"message": "Email confirmed"}
