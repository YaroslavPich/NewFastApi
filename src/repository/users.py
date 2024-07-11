from typing import Optional
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

hash_handler = Hash()


class UsernameTaken(Exception):
    """Exception raised when the username is already taken."""
    pass


class LoginFailed(Exception):
    """Exception raised when login fails due to incorrect credentials."""
    pass


class InvalidRefreshToken(Exception):
    """Exception raised when the refresh token is invalid."""
    pass


class UserService:
    """Service class for user-related operations."""

    @staticmethod
    async def get_user(username: str, db: AsyncSession) -> Optional[User]:
        """
        Retrieve a user by their username.

        :param username: The username of the user to retrieve.
        :type username: str
        :param db: The database session.
        :type db: AsyncSession
        :return: The user if found, otherwise None.
        :rtype: Optional[User]
        """
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().one_or_none()

    @staticmethod
    async def get_user_email(email: str, db: AsyncSession) -> Optional[User]:
        """
        Retrieve a user by their email.

        :param email: The email of the user to retrieve.
        :type email: str
        :param db: The database session.
        :type db: AsyncSession
        :return: The user if found, otherwise None.
        :rtype: Optional[User]
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().one_or_none()

    @staticmethod
    async def check_username_availability(username: str, db: AsyncSession):
        """
        Check if a username is available.

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
        Check if an email is available.

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
        Check if an entered password matches the stored database password.

        :param entered_password: The entered password to verify.
        :type entered_password: str
        :param database_password: The stored database password.
        :type database_password: str
        :raises LoginFailed: If the entered password does not match the stored password.
        """
        if not hash_handler.verify_password(entered_password, database_password):
            raise LoginFailed

    @staticmethod
    async def create_new_user(body: UserModel, db: AsyncSession) -> User:
        """
        Create a new user in the database.

        :param body: The user model containing user details.
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
    async def login_user(body: OAuth2PasswordRequestForm, db: AsyncSession) -> tuple[str, str]:
        """
        Login a user and return access and refresh tokens.

        :param body: The login form containing username and password.
        :type body: OAuth2PasswordRequestForm
        :param db: The database session.
        :type db: AsyncSession
        :return: The access and refresh tokens.
        :rtype: tuple[str, str]
        :raises LoginFailed: If login fails due to incorrect credentials.
        """
        user = await UserService.get_user(body.username, db=db)
        if not user:
            raise LoginFailed
        data = {"sub": user.email}
        UserService.check_password(body.password, user.hashed_password)
        access_token = await create_access_token(data=data)
        refresh_token = await create_refresh_token(data=data)
        user.refresh_token = refresh_token
        await UserService.save_user(user, db)
        return access_token, refresh_token

    @staticmethod
    async def refresh_token(refresh_token: str, db: AsyncSession) -> str:
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
        Save a user to the database.

        :param user_to_save: The user to save.
        :type user_to_save: User
        :param db: The database session.
        :type db: AsyncSession
        :return: The saved user.
        :rtype: User
        """
        db.add(user_to_save)
        await db.commit()
        await db.refresh(user_to_save)
        return user_to_save
