"""Add avatar_url to users table

Revision ID: 9650857e6e5d
Revises: 38cf746f39d8
Create Date: 2024-07-03 22:11:25.739376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9650857e6e5d'
down_revision: Union[str, None] = '38cf746f39d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	pass


def downgrade() -> None:
	pass
