from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: Optional[str] = None


class ContactCreate(ContactBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    birthday: Optional[str] = None


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    birthday: Optional[date] = None
    additional_info: Optional[str] = None


class ContactInDB(ContactBase):
    id: int

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserDisplayModel(BaseModel):
    username: str
    avatar_url: str


class RequestEmail(BaseModel):
    email: EmailStr
