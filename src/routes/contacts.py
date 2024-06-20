from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from src.sсhemas import ContactCreate, ContactUpdate, ContactInDB
from src.repository import contacts as repository_contacts
from src.database.database import get_db
from src.database.models import Contact

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.post("/", response_model=ContactInDB)
async def create_contact(contact: ContactCreate, db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(Contact).filter(Contact.email == contact.email))
	existing_contact = result.scalar()
	if existing_contact:
		raise HTTPException(status_code=400, detail="Email already exists")

	result = await db.execute(select(Contact).filter(Contact.phone_number == contact.phone_number))
	existing_contact = result.scalar()
	if existing_contact:
		raise HTTPException(status_code=400, detail="Phone already exists")

	db_contact = await repository_contacts.create_contact(db, contact)
	if db_contact is None:
		raise HTTPException(status_code=500, detail="Internal Server Error")
	return db_contact


@router.get("/", response_model=List[ContactInDB])
async def read_contacts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
	contacts = await repository_contacts.get_contacts(db, skip=skip, limit=limit)
	return contacts


@router.get("/{contact_id}", response_model=ContactInDB)
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
	db_contact = await repository_contacts.get_contact(db, contact_id)
	if db_contact is None:
		raise HTTPException(status_code=404, detail="Contact not found")
	return db_contact


@router.put("/{contact_id}", response_model=ContactInDB)
async def update_contact(contact_id: int, contact: ContactUpdate, db: AsyncSession = Depends(get_db)):
	db_contact = await repository_contacts.get_contact(db, contact_id)
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

	updated_contact = await repository_contacts.update_contact(db, contact_id, contact)
	if updated_contact is None:
		raise HTTPException(status_code=500, detail="Internal Server Error")
	return updated_contact


@router.delete("/{contact_id}", response_model=ContactInDB)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
	db_contact = await repository_contacts.delete_contact(db, contact_id)
	if db_contact is None:
		raise HTTPException(status_code=404, detail="Contact not found")
	return db_contact


@router.get("/search/", response_model=List[ContactInDB])
async def search_contacts(query: str, db: AsyncSession = Depends(get_db)):
	return await repository_contacts.search_contacts(db, query)


@router.get("/birthdays/", response_model=List[ContactInDB])
async def read_contacts_with_birthdays(db: AsyncSession = Depends(get_db)):
	return await repository_contacts.get_birthdays_within_next_week(db)
