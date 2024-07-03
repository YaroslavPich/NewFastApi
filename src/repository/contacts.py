from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate
from datetime import datetime, timedelta
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select


async def get_contact(db: AsyncSession, contact_id: int, user_id: int):
    result = await db.execute(
        select(Contact).filter(Contact.user_id == user_id, Contact.id == contact_id)
    )
    return result.scalar()


async def get_contacts(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(Contact).filter(Contact.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_contact_in_db(db: AsyncSession, contact: ContactCreate, user_id: int):
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
):
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


async def delete_contact_in_db(db: AsyncSession, contact_id: int, user_id: int):
    result = await db.execute(
        select(Contact).filter(Contact.user_id == user_id, Contact.id == contact_id)
    )
    db_contact = result.scalar()
    if db_contact is None:
        return None
    await db.delete(db_contact)
    await db.commit()
    return db_contact


async def search_contacts_in_db(db: AsyncSession, user_id: int, query: str):
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


async def get_birthdays_within_next_week(db: AsyncSession, user_id: int):
    today = datetime.today().date()
    next_week = today + timedelta(days=7)
    result = await db.execute(
        select(Contact).filter(
            Contact.user_id == user_id, Contact.birthday.between(today, next_week)
        )
    )
    return result.scalars().all()
