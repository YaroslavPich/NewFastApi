"""Create tables

Revision ID: 38cf746f39d8
Revises: 8c1ccb8fc86a
Create Date: 2024-06-24 18:51:37.182097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38cf746f39d8'
down_revision: Union[str, None] = '8c1ccb8fc86a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###