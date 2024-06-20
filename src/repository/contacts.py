from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact
from src.sсhemas import ContactCreate, ContactUpdate
from datetime import datetime, timedelta
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select


async def get_contact(db: AsyncSession, contact_id: int):
	result = await db.execute(select(Contact).filter(Contact.id == contact_id))
	return result.scalar()


async def get_contacts(db: AsyncSession, skip: int = 0, limit: int = 10):
	result = await db.execute(select(Contact).offset(skip).limit(limit))
	return result.scalars().all()


async def create_contact(db: AsyncSession, contact: ContactCreate):
	try:
		db_contact = Contact(**contact.dict())
		db.add(db_contact)
		await db.commit()
		await db.refresh(db_contact)
		return db_contact
	except IntegrityError:
		await db.rollback()
		return None


async def update_contact(db: AsyncSession, contact_id: int, contact: ContactUpdate):
	try:
		result = await db.execute(select(Contact).filter(Contact.id == contact_id))
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


async def delete_contact(db: AsyncSession, contact_id: int):
	result = await db.execute(select(Contact).filter(Contact.id == contact_id))
	db_contact = result.scalar()
	if db_contact is None:
		return None
	await db.delete(db_contact)
	await db.commit()
	return db_contact


async def search_contacts(db: AsyncSession, query: str):
	result = await db.execute(
		select(Contact).filter(
			or_(
				Contact.first_name.ilike(f"%{query}%"),
				Contact.last_name.ilike(f"%{query}%"),
				Contact.email.ilike(f"%{query}%")
			)
		)
	)
	return result.scalars().all()


async def get_birthdays_within_next_week(db: AsyncSession):
	today = datetime.today().date()
	next_week = today + timedelta(days=7)
	result = await db.execute(
		select(Contact).filter(
			Contact.birthday.between(today, next_week)
		)
	)
	return result.scalars().all()
