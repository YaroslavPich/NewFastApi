from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from src.schemas import UserModel
from src.database.database import get_db
from src.repository.users import UserService, UsernameTaken, LoginFailed
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/users', tags=["users"])

user_service = UserService()

security = HTTPBearer()


@router.post("/signup", response_class=JSONResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, db: AsyncSession = Depends(get_db)):
	try:
		new_user = await user_service.create_new_user(body, db)
	except UsernameTaken:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User or email already exist")
	user_data = {"new_user": new_user.username, "Email": new_user.email}
	return user_data


@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
	try:
		access_token, refresh_token = await user_service.login_user(body, db)
	except LoginFailed:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid credentials")
	user_data = {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
	return user_data


@router.post('/refresh_token', response_class=JSONResponse, status_code=status.HTTP_201_CREATED)
async def refresh_token(
		credentials: HTTPAuthorizationCredentials = Security(security),
		db: AsyncSession = Depends(get_db)
):
	token = credentials.credentials
	access_token = await user_service.refresh_token(token, db)
	return {"access_token": access_token, "refresh_token": token, "token_type": "bearer"}
