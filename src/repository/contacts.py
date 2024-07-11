from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate
from datetime import datetime, timedelta
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from typing import Optional


async def get_contact(db: AsyncSession, contact_id: int, user_id: int) -> Optional[Contact]:
	"""
	Retrieve a contact by its ID and user ID.

	:param db: The database session.
	:type db: AsyncSession
	:param contact_id: The ID of the contact to retrieve.
	:type contact_id: int
	:param user_id: The ID of the user who owns the contact.
	:type user_id: int
	:return: The contact if found, otherwise None.
	:rtype: Optional[Contact]
	"""
	result = await db.execute(
		select(Contact).filter(Contact.user_id == user_id, Contact.id == contact_id)
	)
	return result.scalar()


async def get_contacts(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10) -> list[Contact]:
	"""
	Retrieve a list of contacts for a user with pagination.

	:param db: The database session.
	:type db: AsyncSession
	:param user_id: The ID of the user who owns the contacts.
	:type user_id: int
	:param skip: The number of contacts to skip.
	:type skip: int
	:param limit: The maximum number of contacts to return.
	:type limit: int
	:return: A list of contacts.
	:rtype: list[Contact]
	"""
	result = await db.execute(
		select(Contact).filter(Contact.user_id == user_id).offset(skip).limit(limit)
	)
	return result.scalars().all()


async def create_contact_in_db(db: AsyncSession, contact: ContactCreate, user_id: int) -> Optional[Contact]:
	"""
	Create a new contact in the database.

	:param db: The database session.
	:type db: AsyncSession
	:param contact: The contact data to create.
	:type contact: ContactCreate
	:param user_id: The ID of the user who owns the contact.
	:type user_id: int
	:return: The created contact if successful, otherwise None.
	:rtype: Optional[Contact]
	"""
	try:
		db_contact = Contact(**contact.dict(), user_id=user_id)
		db.add(db_contact)
		await db.commit()
		await db.refresh(db_contact)
		return db_contact
	except IntegrityError:
		await db.rollback()
		return None


async def update_contact_in_db(
		db: AsyncSession, user_id: int, contact_id: int, contact: ContactUpdate
) -> Optional[Contact]:
	"""
	Update an existing contact in the database.

	:param db: The database session.
	:type db: AsyncSession
	:param user_id: The ID of the user who owns the contact.
	:type user_id: int
	:param contact_id: The ID of the contact to update.
	:type contact_id: int
	:param contact: The contact data to update.
	:type contact: ContactUpdate
	:return: The updated contact if successful, otherwise None.
	:rtype: Optional[Contact]
	"""
	try:
		result = await db.execute(
			select(Contact).filter(Contact.user_id == user_id, Contact.id == contact_id)
		)
		db_contact = result.scalar()
		if db_contact is None:
			return None
		for key, value in contact.dict().items():
			setattr(db_contact, key, value)
		await db.commit()
		await db.refresh(db_contact)
		return db_contact
	except IntegrityError:
		await db.rollback()
		return None


async def delete_contact_in_db(db: AsyncSession, contact_id: int, user_id: int) -> Optional[Contact]:
	"""
	Delete a contact from the database.

	:param db: The database session.
	:type db: AsyncSession
	:param contact_id: The ID of the contact to delete.
	:type contact_id: int
	:param user_id: The ID of the user who owns the contact.
	:type user_id: int
	:return: The deleted contact if successful, otherwise None.
	:rtype: Optional[Contact]
	"""
	result = await db.execute(
		select(Contact).filter(Contact.user_id == user_id, Contact.id == contact_id)
	)
	db_contact = result.scalar()
	if db_contact is None:
		return None
	await db.delete(db_contact)
	await db.commit()
	return db_contact


async def search_contacts_in_db(db: AsyncSession, user_id: int, query: str) -> list[Contact]:
	"""
	Search for contacts by a query string.

	:param db: The database session.
	:type db: AsyncSession
	:param user_id: The ID of the user who owns the contacts.
	:type user_id: int
	:param query: The query string to search for.
	:type query: str
	:return: A list of contacts matching the query.
	:rtype: list[Contact]
	"""
	result = await db.execute(
		select(Contact)
		.filter(Contact.user_id == user_id)
		.filter(
			or_(
				Contact.first_name.ilike(f"%{query}%"),
				Contact.last_name.ilike(f"%{query}%"),
				Contact.email.ilike(f"%{query}%"),
			)
		)
	)
	return result.scalars().all()


async def get_birthdays_within_next_week(db: AsyncSession, user_id: int) -> list[Contact]:
	"""
	Get contacts with birthdays within the next week.

	:param db: The database session.
	:type db: AsyncSession
	:param user_id: The ID of the user who owns the contacts.
	:type user_id: int
	:return: A list of contacts with upcoming birthdays.
	:rtype: list[Contact]
	"""
	today = datetime.today().date()
	next_week = today + timedelta(days=7)
	result = await db.execute(
		select(Contact).filter(
			Contact.user_id == user_id, Contact.birthday.between(today, next_week)
		)
	)
	return result.scalars().all()
