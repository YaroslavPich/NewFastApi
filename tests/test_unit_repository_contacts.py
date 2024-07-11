import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import ContactBase
from src.database.models import Contact, User


class TestAsyncAuth(unittest.IsolatedAsyncioTestCase):
	def setUp(self):
		self.user = User(id=1, username='test_user', password='qwer', confirmed=True)
		self.session = AsyncMock(spec=AsyncSession)

	async def test_get_contacts(self):