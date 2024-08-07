from datetime import datetime, timedelta, timezone
from typing import Optional
import pickle
import aioredis

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from starlette import status

from src.database.models import User
from src.database.database import get_db, get_redis_client
from src.settings import SECRET_KEY, ALGORITHM, oauth2_scheme

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    """
    A class for password hashing and verification.

    Methods
    -------
    verify_password(plain_password, hashed_password)
        Verifies a plain password against a hashed password.

    get_password_hash(password: str)
        Hashes a plain password.
    """

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """
        Verifies a plain password against a hashed password.

        :param plain_password: The plain password to verify.
        :type plain_password: str
        :param hashed_password: The hashed password to verify against.
        :type hashed_password: str
        :return: True if the password matches, False otherwise.
        :rtype: bool
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str):
        """
        Hashes a plain password.

        :param password: The plain password to hash.
        :type password: str
        :return: The hashed password.
        :rtype: str
        """
        return pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta: Optional[float] = None):
    """
    Creates a new access token.

    :param data: The data to encode in the token.
    :type data: dict
    :param expires_delta: The expiration time in seconds, defaults to 15 minutes.
    :type expires_delta: float, optional
    :return: The encoded access token.
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update(
        {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"}
    )
    encoded_access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_access_token


async def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    """
    Creates a new refresh token.

    :param data: The data to encode in the token.
    :type data: dict
    :param expires_delta: The expiration time in seconds, defaults to 7 days.
    :type expires_delta: float, optional
    :return: The encoded refresh token.
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update(
        {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"}
    )
    encoded_refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
        redis_client: aioredis.Redis = Depends(get_redis_client)
):
    """
    Retrieves the current user based on the provided access token.

    :param token: The access token.
    :type token: str
    :param db: The database session.
    :type db: AsyncSession
    :param redis_client: The Redis client.
    :type redis_client: aioredis.Redis
    :return: The current user.
    :rtype: User
    :raises HTTPException: If the credentials are invalid or the token is expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        exp = payload.get("exp")
        if email is None:
            raise credentials_exception
        if exp is None or exp <= int(datetime.now(timezone.utc).timestamp()):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    redis_key = f"User data: {email}"

    user_data = await redis_client.get(redis_key)

    if user_data is None:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        await redis_client.setex(redis_key, 15 * 60, pickle.dumps(user))
    else:
        user: User = pickle.loads(user_data)

    return user


async def get_email_form_refresh_token(refresh_token: str):
    """
    Retrieves the email from the refresh token.

    :param refresh_token: The refresh token.
    :type refresh_token: str
    :return: The email associated with the refresh token.
    :rtype: str
    :raises HTTPException: If the token is invalid or the scope is incorrect.
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload["scope"] == "refresh_token":
            email = payload["sub"]
            exp = payload["exp"]
            if exp is None or exp <= int(datetime.now(timezone.utc).timestamp()):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return email

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def create_email_token(data: dict):
    """
    Creates a new email token.

    :param data: The data to encode in the token.
    :type data: dict
    :return: The encoded email token.
    :rtype: str
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """
    Retrieves the email from the token.

    :param token: The token.
    :type token: str
    :return: The email associated with the token.
    :rtype: str
    :raises HTTPException: If the token is invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["sub"]
        return email
    except JWTError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid token for email verification"
        )
