from fastapi import APIRouter, Depends, HTTPException, status, Security, Request
from src.schemas import RequestEmail
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from src.database.database import get_db
from src.repository.users import UserService
from src.repository.auth import get_email_from_token, create_email_token, Hash
from celery_worker import send_email

router = APIRouter(prefix="/auth", tags=["auth"])

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
    user = await UserService.get_user_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        await send_email(user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await get_email_from_token(token)
    user = await UserService.get_user_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await UserService.confirmed_email(email, db)
    return {"message": "Email confirmed"}
