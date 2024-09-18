import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession


class StockOut(Base):
    __tablename__ = "stock_outs"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    barcode_id = Column(sq.Integer, ForeignKey("barcodes.id"), nullable=False)
    order_id = Column(sq.Integer, ForeignKey("orders.id"))
    quantity = Column(sq.Integer, nullable=False)
    cost = Column(sq.Float, nullable=True)
    barcode = relationship("Barcode", back_populates="stock_out")
    orders = relationship("Orders", back_populates="stock_out")
    created_at = Column(sq.DateTime, default=datetime.datetime.now())

    def save(self) -> "StockOut":
        with DBSession() as db:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def json(self):
        return {
            "id": self.id,
            "quantity": self.quantity,
            "barcode": self.barcode.json(),
            "cost": self.cost,
            "created_at": self.created_at.isoformat(),
        }
