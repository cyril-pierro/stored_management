import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession
from models.staff import Staff


class PurchaseOrderItems(Base):
    __tablename__ = "purchase_order_items"
    id = Column(sq.Integer, primary_key=True, unique=True, nullable=False)
    barcode_id = Column(sq.Integer, ForeignKey("barcodes.id"), nullable=False)
    supplier_code = Column(sq.String, nullable=False)
    quantity = Column(sq.Integer, nullable=False)
    price = Column(sq.Float, nullable=False)
    sub_total = Column(sq.Float, nullable=False)

    purchase_order_id = Column(
        sq.Integer, ForeignKey("purchase_orders.id"), nullable=False
    )
    requested_by = Column(sq.Integer, ForeignKey("staffs.id"), nullable=False)

    requested_by_staff = relationship(Staff, back_populates="purchase_order_items")
    barcode = relationship("Barcode", back_populates="purchase_order_items")
    purchase_orders = relationship(
        "PurchaseOrders",
        back_populates="purchase_order_items",
        passive_deletes="all",
        passive_updates=True,
    )

    created_at = Column(sq.DateTime, default=datetime.datetime.now())
    updated_at = Column(sq.DateTime, onupdate=datetime.datetime.now())

    def save(self, merge=False) -> "PurchaseOrderItems":
        with DBSession() as db:
            if merge:
                self = db.merge(self)
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def delete(self, force=False) -> bool:
        with DBSession() as db:
            if force:
                self = db.merge(self)
            db.delete(self)
            db.commit()
            return True

    def json(self):
        return {
            "id": self.id,
            "purchase_order_id": self.purchase_order_id,
            "barcode_id": self.barcode_id,
            "supplier_code": self.supplier_code,
            "quantity": self.quantity,
            "price": self.price,
            "sub_total": self.sub_total,
            "created_at": self.created_at.isoformat(),
        }
