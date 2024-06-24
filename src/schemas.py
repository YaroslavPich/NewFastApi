from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class ContactBase(BaseModel):
	first_name: str
	last_name: str
	email: EmailStr
	phone_number: str
	birthday: Optional[date] = None
	additional_info: Optional[str] = None


class ContactCreate(ContactBase):
	pass


class ContactUpdate(ContactBase):
	pass


class ContactInDB(ContactBase):
	id: int
	user_id: int

	class Config:
		orm_mode = True


class UserBase(BaseModel):
	email: EmailStr


class UserCreate(UserBase):
	password: str


class UserInDB(UserBase):
	id: int

	class Config:
		orm_mode = True


class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	email: Optional[str] = None
