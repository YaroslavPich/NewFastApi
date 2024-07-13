from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException
from fastapi_limiter.depends import RateLimiter

from src.schemas import ContactCreate, ContactUpdate, ContactInDB
from src.repository.contacts import (
    get_contacts,
    get_contact,
    update_contact_in_db,
    delete_contact_in_db,
    search_contacts_in_db,
    get_birthdays_within_next_week,
    create_contact_in_db,
)
from src.database.database import get_db
from src.database.models import Contact, User
from src.repository.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ContactInDB, dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create a new contact for the authenticated user.

    Raises HTTP 400 if email or phone number already exists.

    :param contact: Contact data to create.
    :type contact: ContactCreate
    :param db: Async database session.
    :type db: AsyncSession
    :param user: Current authenticated user.
    :type user: User
    :return: Created contact data.
    :rtype: ContactInDB
    """
    result = await db.execute(select(Contact).filter(Contact.email == contact.email))
    existing_contact = result.scalar()
    if existing_contact:
        raise HTTPException(status_code=400, detail="Email already exists")

    result = await db.execute(select(Contact).filter(Contact.phone_number == contact.phone_number))
    existing_contact = result.scalar()
    if existing_contact:
        raise HTTPException(status_code=400, detail="Phone already exists")

    db_contact = await create_contact_in_db(db, contact, user.id)
    if db_contact is None:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return db_contact


@router.get("/", response_model=List[ContactInDB], dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def read_contacts(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Retrieve a list of contacts for the authenticated user.

    :param skip: Number of contacts to skip (default: 0).
    :type skip: int
    :param limit: Maximum number of contacts to return (default: 10).
    :type limit: int
    :param db: Async database session.
    :type db: AsyncSession
    :param user: Current authenticated user.
    :type user: User
    :return: List of contacts.
    :rtype: List[ContactInDB]
    """
    contacts = await get_contacts(db, user_id=user.id, skip=skip, limit=limit)
    return contacts


@router.get("/{contact_id}", response_model=ContactInDB, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Retrieve a specific contact by ID for the authenticated user.

    :param contact_id: ID of the contact to retrieve.
    :type contact_id: int
    :param db: Async database session.
    :type db: AsyncSession
    :param user: Current authenticated user.
    :type user: User
    :return: Contact data.
    :rtype: ContactInDB
    """
    db_contact = await get_contact(db, contact_id, user_id=user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.get(
    "/search/",
    response_model=List[ContactInDB],
    dependencies=[Depends(RateLimiter(times=1, seconds=20))]
)
async def search_contacts(
    query: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Search contacts by query string for the authenticated user.

    :param query: Search query string.
    :type query: str
    :param db: Async database session.
    :type db: AsyncSession
    :param user: Current authenticated user.
    :type user: User
    :return: List of contacts matching the query.
    :rtype: List[ContactInDB]
    """
    return await search_contacts_in_db(db, user_id=user.id, query=query)


@router.get("/birthdays/", response_model=List[ContactInDB], dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def read_contacts_with_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Retrieve contacts with birthdays within the next week for the authenticated user.

    :param db: Async database session.
    :type db: AsyncSession
    :param user: Current authenticated user.
    :type user: User
    :return: List of contacts with upcoming birthdays.
    :rtype: List[ContactInDB]
    """
    return await get_birthdays_within_next_week(db, user_id=user.id)


@router.put("/{contact_id}", response_model=ContactInDB)
async def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Update a specific contact by ID for the authenticated user.

    Raises HTTP 400 if email or phone number already exists.

    :param contact_id: ID of the contact to update.
    :type contact_id: int
    :param contact: Contact data to update.
    :type contact: ContactUpdate
    :param db: Async database session.
    :type db: AsyncSession
    :param user: Current authenticated user.
    :type user: User
    :return: Updated contact data.
    :rtype: ContactInDB
    """
    db_contact = await get_contact(db, contact_id, user_id=user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    if contact.email:
        result = await db.execute(select(Contact).filter(Contact.email == contact.email, Contact.id != contact_id))
        existing_contact = result.scalar()
        if existing_contact:
            raise HTTPException(status_code=400, detail="Email already exists")

    if contact.phone_number:
        result = await db.execute(
            select(Contact).filter(Contact.phone_number == contact.phone_number, Contact.id != contact_id))
        existing_contact = result.scalar()
        if existing_contact:
            raise HTTPException(status_code=400, detail="Phone already exists")

    updated_contact = await update_contact_in_db(db, user_id=user.id, contact_id=contact_id, contact=contact)
    if updated_contact is None:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return updated_contact


@router.delete("/{contact_id}", response_model=ContactInDB)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Delete a specific contact by ID for the authenticated user.

    :param contact_id: ID of the contact to delete.
    :type contact_id: int
    :param db: Async database session.
    :type db: AsyncSession
    :param user: Current authenticated user.
    :type user: User
    :return: Deleted contact data.
    :rtype: ContactInDB
    """
    db_contact = await delete_contact_in_db(db, contact_id, user_id=user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact
