"""add category id

Revision ID: 7a2af8d96d8e
Revises: f0a7513d9f51
Create Date: 2024-09-14 00:20:53.608824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a2af8d96d8e'
down_revision: Union[str, None] = 'f0a7513d9f51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('barcode', 'category_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_foreign_key("fkey_barcode_categories", 'barcode', 'categories', ['category_id'], ['id'])
    op.drop_column('barcode', 'category')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('barcode', sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint("fkey_barcode_categories", 'barcode', type_='foreignkey')
    op.alter_column('barcode', 'category_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
