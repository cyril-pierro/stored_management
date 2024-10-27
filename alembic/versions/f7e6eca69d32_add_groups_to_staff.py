"""add groups to staff

Revision ID: f7e6eca69d32
Revises: 5da1705e0265
Create Date: 2024-10-24 13:37:20.196628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f7e6eca69d32'
down_revision: Union[str, None] = '5da1705e0265'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    banner_status = postgresql.ENUM('managers', 'users', name='groupstates')
    banner_status.create(op.get_bind())
    op.add_column('groups', sa.Column('group', sa.Enum('managers', 'users', name='groupstates'), nullable=True))
    op.drop_index('ix_groups_name', table_name='groups')
    op.drop_column('groups', 'name')
    
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('groups', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_index('ix_groups_name', 'groups', ['name'], unique=False)
    op.drop_column('groups', 'group')
    # ### end Alembic commands ###
