import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.enum import RunningStockStatus
from utils.session import DBSession


class StockRunning(Base):
    __tablename__ = "stock_running"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    out_quantity = Column(sq.Integer, nullable=False)
    adjustment_quantity = Column(sq.Integer, nullable=False)
    remaining_quantity = Column(sq.Integer, nullable=False)
    status = Column(
        sq.Enum(RunningStockStatus), default=RunningStockStatus.available.name
    )
    stock_id = Column(sq.Integer, ForeignKey("stock.id"))
    stock = relationship("Stock", back_populates="stock_running")
    created_at = Column(sq.DateTime, default=datetime.datetime.now(datetime.UTC))

    def save(self) -> "StockRunning":
        with DBSession() as db:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def json(self):
        return {
            "id": self.id,
            "out_quantity": self.out_quantity,
            "adjustment_quantity": self.adjustment_quantity,
            "remaining_quantity": self.remaining_quantity,
            "status": self.status.value,
            "stock": self.stock.json(),
            "created_at": self.created_at.isoformat(),
        }
