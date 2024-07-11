from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate
from datetime import datetime, timedelta
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select


async def get_contact(db: AsyncSession, contact_id: int, user_id: int):
    """
    Retrieve a contact by ID for a specific user.

    :param db: The database session.
    :type db: AsyncSession
    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user_id: The ID of the user to whom the contact belongs.
    :type user_id: int
    :return: The retrieved contact or None if not found.
    :rtype: Contact or None
    """
    result = await db.execute(
        select(Contact).filter(Contact.user_id == user_id, Contact.id == contact_id)
    )
    return result.scalar()


async def get_contacts(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    """
    Retrieve a list of contacts for a specific user with pagination.

    :param db: The database session.
    :type db: AsyncSession
    :param user_id: The ID of the user to whom the contacts belong.
    :type user_id: int
    :param skip: The number of contacts to skip. Default is 0.
    :type skip: int
    :param limit: The maximum number of contacts to return. Default is 10.
    :type limit: int
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    result = await db.execute(
        select(Contact).filter(Contact.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_contact_in_db(db: AsyncSession, contact: ContactCreate, user_id: int):
    """
    Create a new contact in the database.

    :param db: The database session.
    :type db: AsyncSession
    :param contact: The contact data to create.
    :type contact: ContactCreate
    :param user_id: The ID of the user to whom the contact will belong.
    :type user_id: int
    :return: The created contact or None if an integrity error occurs.
    :rtype: Contact or None
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
):
    """
    Update an existing contact in the database.

    :param db: The database session.
    :type db: AsyncSession
    :param user_id: The ID of the user to whom the contact belongs.
    :type user_id: int
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param contact: The updated contact data.
    :type contact: ContactUpdate
    :return: The updated contact or None if not found or an integrity error occurs.
    :rtype: Contact or None
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


async def delete_contact_in_db(db: AsyncSession, contact_id: int, user_id: int):
    """
    Delete a contact from the database.

    :param db: The database session.
    :type db: AsyncSession
    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param user_id: The ID of the user to whom the contact belongs.
    :type user_id: int
    :return: The deleted contact or None if not found.
    :rtype: Contact or None
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


async def search_contacts_in_db(db: AsyncSession, user_id: int, query: str):
    """
    Search for contacts in the database.

    :param db: The database session.
    :type db: AsyncSession
    :param user_id: The ID of the user to whom the contacts belong.
    :type user_id: int
    :param query: The search query.
    :type query: str
    :return: A list of contacts that match the search query.
    :rtype: List[Contact]
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


async def get_birthdays_within_next_week(db: AsyncSession, user_id: int):
    """
    Retrieve contacts with birthdays within the next week.

    :param db: The database session.
    :type db: AsyncSession
    :param user_id: The ID of the user to whom the contacts belong.
    :type user_id: int
    :return: A list of contacts with birthdays within the next week.
    :rtype: List[Contact]
    """
    today = datetime.today().date()
    next_week = today + timedelta(days=7)
    result = await db.execute(
        select(Contact).filter(
            Contact.user_id == user_id, Contact.birthday.between(today, next_week)
        )
    )
    return result.scalars().all()
