import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.enum import RunningStockStatus
from utils.session import DBSession


class StockRunning(Base):
    __tablename__ = "stock_runnings"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    barcode_id = Column(sq.Integer, ForeignKey("barcodes.id"), nullable=False)
    stock_quantity = Column(sq.Integer, nullable=False)
    out_quantity = Column(sq.Integer, nullable=False, default=0)
    adjustment_quantity = Column(sq.Integer, nullable=False, default=0)
    remaining_quantity = Column(sq.Integer, nullable=False)
    status = Column(
        sq.Enum(RunningStockStatus), default=RunningStockStatus.available.name
    )
    barcode = relationship("Barcode", back_populates="stock_running", lazy="selectin")
    created_at = Column(sq.DateTime, default=datetime.datetime.now())
    updated_at = Column(sq.DateTime)

    def save(self, merge=False) -> "StockRunning":
        with DBSession() as db:
            if merge:
                self = db.merge(self)
            self.updated_at = datetime.datetime.now()
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def json(self):
        return {
            "id": self.id,
            "stock_quantity": self.stock_quantity,
            "out_quantity": self.out_quantity,
            "adjustment_quantity": self.adjustment_quantity,
            "remaining_quantity": self.remaining_quantity,
            "status": self.status.value,
            "barcode": self.barcode.json(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
