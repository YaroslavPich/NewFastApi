from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile

from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from src.schemas import UserModel, UserDisplayModel
from src.database.models import User
from src.database.database import get_db
from src.repository.users import UserService, UsernameTaken, LoginFailed
from fastapi.responses import JSONResponse
from celery_worker import send_test_email_task, send_email
from src.repository.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

user_service = UserService()

security = HTTPBearer()


@router.post(
    "/signup", response_class=JSONResponse, status_code=status.HTTP_201_CREATED
)
async def signup(body: UserModel, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        new_user = await UserService.create_new_user(body, db)
        await send_email(new_user.email, new_user.username, str(request.base_url))
    except UsernameTaken:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User or email already exist"
        )
    user_data = {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}
    return user_data


@router.post("/login")
async def login(
        body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    try:
        access_token, refresh_token = await UserService.login_user(body, db)
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


@router.post('/send_test_email')
async def send_test_email(email_to_send: str):
    send_test_email_task.delay(email_to_send)


@router.patch('/avatar', response_model=UserDisplayModel)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_db)):
    user = UserService.update_avatar(current_user, file, db)
    return user