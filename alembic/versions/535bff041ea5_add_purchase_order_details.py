"""add purchase order details

Revision ID: 535bff041ea5
Revises: 166995855332
Create Date: 2024-10-16 11:28:31.164037

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "535bff041ea5"
down_revision: Union[str, None] = "166995855332"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "purchase_order_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "purchase_order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("barcode_id", sa.Integer(), nullable=False),
        sa.Column("supplier_code", sa.String(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("sub_total", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["barcode_id"],
            ["barcodes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("supplier_name", sa.String(), nullable=False),
        sa.Column("payment_terms", sa.String(), nullable=False),
        sa.Column(
            "state",
            sa.Enum("draft", "sent", "validate", name="purchaseorderstates"),
            nullable=False,
        ),
        sa.Column("order_type_id", sa.Integer(), nullable=False),
        sa.Column("purchase_order_item_ids", sa.Integer(), nullable=False),
        sa.Column("requested_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["order_type_id"],
            ["purchase_order_types.id"],
        ),
        sa.ForeignKeyConstraint(
            ["purchase_order_item_ids"],
            ["purchase_order_items.id"],
        ),
        sa.ForeignKeyConstraint(
            ["requested_by"],
            ["staffs.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("purchase_orders")
    op.drop_table("purchase_order_items")
    op.drop_table("purchase_order_types")
    # ### end Alembic commands ###
