from typing import Optional
from fastapi import UploadFile
from src.repository.auth import (
    Hash,
    create_access_token,
    create_refresh_token,
    get_email_form_refresh_token,
)
from src.database.models import User
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.schemas import UserModel
from src.utils.cloudinary import upload_file_to_cloudinary

hash_handler = Hash()


class UsernameTaken(Exception):
    pass


class LoginFailed(Exception):
    pass


class InvalidRefreshToken(Exception):
    pass


class UserService:
    @staticmethod
    async def get_user(username: str, db: AsyncSession) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().one_or_none()

    @staticmethod
    async def get_user_email(email: str, db: AsyncSession) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().one_or_none()

    @staticmethod
    async def check_username_availability(username: str, db: AsyncSession):
        exist_user = await UserService.get_user(username, db)
        if exist_user:
            raise UsernameTaken

    @staticmethod
    async def check_username_email_availability(email: str, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == email))
        exist_user = result.scalar_one_or_none()
        if exist_user:
            raise UsernameTaken

    @staticmethod
    def check_password(entered_password: str, database_password: str):
        if not hash_handler.verify_password(entered_password, database_password):
            raise LoginFailed

    @staticmethod
    async def create_new_user(body: UserModel, db: AsyncSession):
        await UserService.check_username_availability(username=body.username, db=db)
        await UserService.check_username_email_availability(email=body.email, db=db)
        new_user = User(
            username=body.username,
            email=body.email,
            hashed_password=hash_handler.get_password_hash(body.password),
        )
        new_user = await UserService.save_user(new_user, db)
        return new_user

    @staticmethod
    async def login_user(body: OAuth2PasswordRequestForm, db: AsyncSession):
        user = await UserService.get_user(body.username, db=db)
        if not user:
            raise LoginFailed
        if not user.confirmed:
            raise LoginFailed
        data = {"sub": user.email}
        UserService.check_password(body.password, user.hashed_password)
        access_token = await create_access_token(data=data)
        refresh_token = await create_refresh_token(data=data)
        user.refresh_token = refresh_token
        await UserService.save_user(user, db)
        return access_token, refresh_token

    @staticmethod
    async def refresh_token(refresh_token: str, db: AsyncSession):
        email = await get_email_form_refresh_token(refresh_token)
        print(email)
        user = await UserService.get_user_email(email, db=db)
        print(user)
        if user is None:
            raise InvalidRefreshToken()

        if user.refresh_token != refresh_token:
            user.refresh_token = None
            await UserService.save_user(user, db)
            raise InvalidRefreshToken()

        access_token = await create_access_token(data={"sub": email})
        return access_token

    @staticmethod
    async def save_user(user_to_save: User, db: AsyncSession) -> User:
        db.add(user_to_save)
        await db.commit()
        await db.refresh(user_to_save)
        return user_to_save

    @staticmethod
    async def confirmed_email(email: str, db: AsyncSession) -> None:
        user = await UserService.get_user_email(email, db)
        user.confirmed = True
        await db.commit()

    @staticmethod
    def update_avatar(user: User, file: UploadFile, db: AsyncSession):
        user.avatar_url = upload_file_to_cloudinary(file.file, f'user avatar{user.id}')
        UserService.save_user(user, db)
        return user
