"""add groups to staff

Revision ID: 5da1705e0265
Revises: e726bd94f2cb
Create Date: 2024-10-24 13:13:55.797206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5da1705e0265'
down_revision: Union[str, None] = 'e726bd94f2cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groups',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_groups_id'), 'groups', ['id'], unique=True)
    op.create_index(op.f('ix_groups_name'), 'groups', ['name'], unique=True)

    op.add_column('staffs', sa.Column('group_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('staffs', 'group_id')
    op.drop_index(op.f('ix_groups_name'), table_name='groups')
    op.drop_index(op.f('ix_groups_id'), table_name='groups')
    op.drop_table('groups')
    # ### end Alembic commands ###