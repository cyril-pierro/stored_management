"""add total cost

Revision ID: bdaed69c3df2
Revises: d38a422a0c21
Create Date: 2024-09-13 12:52:28.650154

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdaed69c3df2'
down_revision: Union[str, None] = 'd38a422a0c21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('total_cost', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'total_cost')
    # ### end Alembic commands ###
