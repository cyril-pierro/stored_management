"""convert supplier_name to supplier_id

Revision ID: 4a60ac9d815d
Revises: 8c3aa1b58f6d
Create Date: 2024-10-30 11:26:26.104267

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a60ac9d815d'
down_revision: Union[str, None] = '8c3aa1b58f6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('suppliers',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    op.add_column('purchase_orders', sa.Column(
        'supplier_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'purchase_orders',
                          'suppliers', ['supplier_id'], ['id'])
    op.drop_column('purchase_orders', 'supplier_name')
   
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('purchase_orders', sa.Column('supplier_name',
                  sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'purchase_orders', type_='foreignkey')
    op.drop_column('purchase_orders', 'supplier_id')
    op.drop_table('suppliers')
    # ### end Alembic commands ###
