"""add data to groups

Revision ID: 45e5361c6aa6
Revises: f7e6eca69d32
Create Date: 2024-10-24 13:50:37.699744

"""
from typing import Sequence, Union

from alembic import op
from models.groups import Groups
from utils.enum import GroupStates
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '45e5361c6aa6'
down_revision: Union[str, None] = 'f7e6eca69d32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.bulk_insert(
        Groups.__table__,
        rows=[
            {
                "id": 1,
                "name": GroupStates.managers.value,
                "created_at": datetime.now()
            },
            {
                "id": 2,
                "name": GroupStates.users.value,
                "created_at": datetime.now()
            }
        ]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
