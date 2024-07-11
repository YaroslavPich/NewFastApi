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
        """
        Retrieve a user by username from the database.

        :param username: The username of the user to retrieve.
        :type username: str
        :param db: The database session.
        :type db: AsyncSession
        :return: The retrieved user or None if not found.
        :rtype: Optional[User]
        """
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().one_or_none()

    @staticmethod
    async def get_user_email(email: str, db: AsyncSession) -> Optional[User]:
        """
        Retrieve a user by email from the database.

        :param email: The email of the user to retrieve.
        :type email: str
        :param db: The database session.
        :type db: AsyncSession
        :return: The retrieved user or None if not found.
        :rtype: Optional[User]
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().one_or_none()

    @staticmethod
    async def check_username_availability(username: str, db: AsyncSession):
        """
        Check if a username is available in the database.

        :param username: The username to check.
        :type username: str
        :param db: The database session.
        :type db: AsyncSession
        :raises UsernameTaken: If the username is already taken.
        """
        exist_user = await UserService.get_user(username, db)
        if exist_user:
            raise UsernameTaken

    @staticmethod
    async def check_username_email_availability(email: str, db: AsyncSession):
        """
        Check if an email is available in the database.

        :param email: The email to check.
        :type email: str
        :param db: The database session.
        :type db: AsyncSession
        :raises UsernameTaken: If the email is already taken.
        """
        result = await db.execute(select(User).where(User.email == email))
        exist_user = result.scalar_one_or_none()
        if exist_user:
            raise UsernameTaken

    @staticmethod
    def check_password(entered_password: str, database_password: str):
        """
        Verify if the entered password matches the database password hash.

        :param entered_password: The password entered by the user.
        :type entered_password: str
        :param database_password: The hashed password stored in the database.
        :type database_password: str
        :raises LoginFailed: If the passwords do not match.
        """
        if not hash_handler.verify_password(entered_password, database_password):
            raise LoginFailed

    @staticmethod
    async def create_new_user(body: UserModel, db: AsyncSession):
        """
        Create a new user in the database.

        :param body: The user data to create.
        :type body: UserModel
        :param db: The database session.
        :type db: AsyncSession
        :return: The created user.
        :rtype: User
        """
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
        """
        Login a user and generate access and refresh tokens.

        :param body: The login form data containing username and password.
        :type body: OAuth2PasswordRequestForm
        :param db: The database session.
        :type db: AsyncSession
        :return: Tuple containing access token and refresh token.
        :rtype: tuple[str, str]
        :raises LoginFailed: If login fails due to invalid credentials.
        """
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
        """
        Refresh an access token using a refresh token.

        :param refresh_token: The refresh token to use.
        :type refresh_token: str
        :param db: The database session.
        :type db: AsyncSession
        :return: The new access token.
        :rtype: str
        :raises InvalidRefreshToken: If the refresh token is invalid.
        """
        email = await get_email_form_refresh_token(refresh_token)
        user = await UserService.get_user_email(email, db=db)
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
        """
        Save or update a user in the database.

        :param user_to_save: The user object to save or update.
        :type user_to_save: User
        :param db: The database session.
        :type db: AsyncSession
        :return: The saved or updated user.
        :rtype: User
        """
        db.add(user_to_save)
        await db.commit()
        await db.refresh(user_to_save)
        return user_to_save

    @staticmethod
    async def confirmed_email(email: str, db: AsyncSession) -> None:
        """
        Confirm a user's email.

        :param email: The email of the user to confirm.
        :type email: str
        :param db: The database session.
        :type db: AsyncSession
        """
        user = await UserService.get_user_email(email, db)
        user.confirmed = True
        await db.commit()

    @staticmethod
    def update_avatar(user: User, file: UploadFile, db: AsyncSession):
        """
        Update a user's avatar by uploading a file to Cloudinary.

        :param user: The user object to update.
        :type user: User
        :param file: The file to upload as the avatar.
        :type file: UploadFile
        :param db: The database session.
        :type db: AsyncSession
        :return: The updated user object.
        :rtype: User
        """
        user.avatar_url = upload_file_to_cloudinary(file.file, f"user_avatar_{user.id}")
        UserService.save_user(user, db)
        return user
