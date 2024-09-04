"""move erm_code to barcode

Revision ID: eb8dec70749b
Revises: 81bf6867e90c
Create Date: 2024-09-04 12:41:04.814690

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb8dec70749b'
down_revision: Union[str, None] = '81bf6867e90c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('barcode', sa.Column('erm_code', sa.String(), nullable=True))
    op.drop_column('stock', 'erm_code')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stock', sa.Column('erm_code', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('barcode', 'erm_code')
    # ### end Alembic commands ###
