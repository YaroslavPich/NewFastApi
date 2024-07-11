"""
START PYTEST!!!!!!!!!!!!!

python -m pytest tests/

"""

import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from src.repository.contacts import (
    create_contact_in_db,
    get_contact,
    update_contact_in_db,
    delete_contact_in_db,
    search_contacts_in_db,
    get_birthdays_within_next_week,
)
from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate


class TestContactFunctions(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = User(id=1, username='test_user', hashed_password='qwerty', confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contact(self):
        contact_id = 1
        user_id = 1
        mocked_contact = Contact(id=contact_id, first_name='John', last_name='Doe', user=self.user)
        mocked_query = MagicMock()
        mocked_query.scalar.return_value = mocked_contact
        self.session.execute.return_value = mocked_query

        result = await get_contact(self.session, contact_id, user_id)

        self.assertEqual(result, mocked_contact)

    async def test_update_contact_in_db(self):
        contact_id = 1
        user_id = 1
        updated_data = ContactUpdate(first_name='Updated John')
        mocked_contact = Contact(id=contact_id, first_name='John', last_name='Doe', user_id=user_id)
        mocked_query = MagicMock()
        mocked_query.scalar.return_value = mocked_contact
        self.session.execute.return_value = mocked_query
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock(return_value=mocked_contact)

        result = await update_contact_in_db(self.session, user_id, contact_id, updated_data)

        self.assertEqual(result.first_name, updated_data.first_name)

    async def test_delete_contact_in_db(self):
        contact_id = 1
        user_id = 1
        mocked_contact = Contact(id=contact_id, first_name='John', last_name='Doe', user_id=user_id)
        mocked_query = MagicMock()
        mocked_query.scalar.return_value = mocked_contact
        self.session.execute.return_value = mocked_query
        self.session.commit = AsyncMock()

        result = await delete_contact_in_db(self.session, contact_id, user_id)

        self.assertEqual(result, mocked_contact)

    async def test_search_contacts_in_db(self):
        user_id = 1
        query = 'Doe'
        mocked_result = [
            Contact(id=1, first_name='John', last_name='Doe', user=self.user),
            Contact(id=2, first_name='Jane', last_name='Doe', user=self.user)
        ]
        mocked_query = MagicMock()
        mocked_query.scalars.return_value.all.return_value = mocked_result
        self.session.execute.return_value = mocked_query

        result = await search_contacts_in_db(self.session, user_id, query)

        self.assertEqual(result, mocked_result)

    async def test_get_birthdays_within_next_week(self):
        user_id = 1
        today = datetime.today().date()
        next_week = today + timedelta(days=7)
        mocked_result = [
            Contact(id=1, first_name='John', last_name='Doe', birthday=today, user=self.user),
            Contact(id=2, first_name='Jane', last_name='Doe', birthday=next_week, user=self.user)
        ]
        mocked_query = MagicMock()
        mocked_query.scalars.return_value.all.return_value = mocked_result
        self.session.execute.return_value = mocked_query

        result = await get_birthdays_within_next_week(self.session, user_id)

        self.assertEqual(result, mocked_result)

    async def test_create_contact_in_db(self):
        body = ContactCreate(first_name='John', last_name='Duo')
        result = await create_contact_in_db(self.session, body, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)


if __name__ == '__main__':
    unittest.main()
