import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession
from utils.enum import PurchaseOrderStates


class PurchaseOrders(Base):
    __tablename__ = "purchase_orders"
    id = Column(sq.Integer, primary_key=True, unique=True, nullable=False)
    state = Column(
        sq.Enum(PurchaseOrderStates),
        nullable=False,
        default=PurchaseOrderStates.draft.value,
    )

    supplier_id = Column(sq.Integer, ForeignKey(
        "suppliers.id"), nullable=False)
    payment_term_id = Column(sq.Integer, ForeignKey(
        "payment_terms.id"), nullable=False)
    order_type_id = Column(
        sq.Integer, ForeignKey("purchase_order_types.id"), nullable=False
    )

    payment_terms = relationship(
        "PaymentTerms", back_populates="purchase_orders")
    purchase_order_types = relationship("PurchaseOrderTypes")
    purchase_order_items = relationship(
        "PurchaseOrderItems", back_populates="purchase_orders", lazy="selectin"
    )
    suppliers = relationship(
        "Suppliers", back_populates="purchase_orders", lazy="selectin")

    created_at = Column(sq.DateTime, default=datetime.datetime.now())
    updated_at = Column(
        sq.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now()
    )

    def save(self, merge=False) -> "PurchaseOrders":
        with DBSession() as db:
            if merge:
                self = db.merge(self)
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def update(self, data: dict) -> "PurchaseOrders":
        with DBSession() as db:
            db.query(PurchaseOrders).filter(
                PurchaseOrders.id == self.id
            ).update(data)
            db.commit()
            value = db.query(PurchaseOrders).filter(
                PurchaseOrders.id == self.id
            ).first()
            return value

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
            "suppliers": self.suppliers,
            "payment_terms": self.payment_terms.name,
            "state": self.state.name,
            "order_type_id": self.order_type_id,
            "order_type": self.purchase_order_types.name,
            "purchase_order_items": self.purchase_order_items,
            "created_at": self.created_at.isoformat(),
        }
