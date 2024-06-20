from typing import List

from fastapi import Depends, HTTPException, APIRouter

from src.shemas import ContactCreate, ContactUpdate, ContactInDB
from src.repository import contacts as repository_contacts
from src.database.models import Contact
from src.database.database import get_db

from sqlalchemy.orm import Session

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.post("/", response_model=ContactInDB)
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
	try:
		if db.query(Contact).filter(Contact.email == contact.email).first():
			raise HTTPException(status_code=400, detail="Email already exists")
		if db.query(Contact).filter(Contact.phone_number == contact.phone_number).first():
			raise HTTPException(status_code=400, detail="Phone already exists")
		return repository_contacts.create_contact(db, contact)
	except HTTPException as e:
		raise e
	except Exception:
		raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/", response_model=List[ContactInDB])
async def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
	contacts = await repository_contacts.get_contacts(db, skip=skip, limit=limit)
	return contacts


@router.get("/{contact_id}", response_model=ContactInDB)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
	db_contact = await repository_contacts.get_contact(db, contact_id)
	if db_contact is None:
		raise HTTPException(status_code=404, detail="Contact not found")
	return db_contact


@router.put("/{contact_id}", response_model=ContactInDB)
async def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
	try:
		db_contact = await repository_contacts.get_contact(db, contact_id)
		if db_contact is None:
			raise HTTPException(status_code=404, detail="Contact not found")
		if contact.email and db.query(Contact).filter(Contact.email == contact.email, Contact.id != contact_id).first():
			raise HTTPException(status_code=400, detail="Email already exists")
		if contact.phone_number and db.query(Contact).filter(Contact.phone_number == contact.phone_number,
		                                                     Contact.id != contact_id).first():
			raise HTTPException(status_code=400, detail="Phone already exists")
		updated_contact = await repository_contacts.update_contact(db, contact_id, contact)
		return updated_contact
	except HTTPException as e:
		raise e
	except Exception:
		raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{contact_id}", response_model=ContactInDB)
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
	db_contact = await repository_contacts.delete_contact(db, contact_id)
	if db_contact is None:
		raise HTTPException(status_code=404, detail="Contact not found")
	return db_contact


@router.get("/search/", response_model=List[ContactInDB])
async def search_contacts(query: str, db: Session = Depends(get_db)):
	return repository_contacts.search_contacts(db, query)


@router.get("/birthdays/", response_model=List[ContactInDB])
async def read_contacts_with_birthdays(db: Session = Depends(get_db)):
	return repository_contacts.get_birthdays_within_next_week(db)
