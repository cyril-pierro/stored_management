import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession


class Barcode(Base):
    __tablename__ = "barcodes"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True, nullable=False)
    barcode = Column(sq.String, unique=True, index=True, nullable=False)
    code = Column(sq.String, index=True, nullable=False)
    specification = Column(sq.String, nullable=False)
    location = Column(sq.String, nullable=False)
    category_id = Column(sq.Integer, ForeignKey("categories.id"), nullable=False)
    erm_code = Column(sq.String, nullable=True)
    category = relationship(
        "Category",
        back_populates="barcode",
        passive_updates=True,
        lazy="selectin"
    )
    stock = relationship(
        "Stock",
        back_populates="barcode",
        passive_deletes="all",
        passive_updates=True,
        lazy="selectin",
    )
    stock_adjustments = relationship(
        "StockAdjustment",
        back_populates="barcode",
        passive_deletes="all",
        passive_updates=True,
        lazy="subquery",
    )
    stock_out = relationship(
        "StockOut",
        back_populates="barcode",
        passive_deletes="all",
        passive_updates=True,
        lazy="subquery",
    )
    stock_running = relationship(
        "StockRunning",
        back_populates="barcode",
        passive_deletes="all",
        passive_updates=True,
        lazy="subquery",
    )
    orders = relationship(
        "Orders",
        back_populates="barcode",
        passive_deletes="all",
        passive_updates=True,
        lazy="subquery",
    )
    cost_evaluation = relationship(
        "CostEvaluation",
        back_populates="barcode",
        passive_deletes="all",
        passive_updates=True,
        lazy="subquery",
    )
    purchase_order_items = relationship(
        "PurchaseOrderItems",
        back_populates="barcode",
        passive_deletes="all",
        passive_updates=True,
        lazy="subquery",
    )
    created_at = Column(sq.DateTime, default=datetime.datetime.now())

    def save(self, merge=False):
        with DBSession() as db:
            if merge:
                self = db.merge(self)
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def json(self):
        return {
            "id": self.id,
            "barcode": self.barcode,
            "code": self.code,
            "specification": self.specification,
            "location": self.location,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
        }

    @staticmethod
    def get_last_stock():
        with DBSession() as db:
            return db.query(Barcode).order_by(Barcode.id.desc()).first()
