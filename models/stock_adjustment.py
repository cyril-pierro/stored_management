import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession


class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    quantity = Column(sq.Integer, nullable=False, default=0)
    stock_id = Column(sq.Integer, ForeignKey("stock.id"))
    department_id = Column(sq.Integer, ForeignKey("department.id"))
    department = relationship("Department", back_populates="stock_adjustments")
    stock = relationship("Stock", back_populates="stock_adjustments")
    created_at = Column(sq.DateTime, default=datetime.datetime.now(datetime.UTC))

    def save(self) -> "StockAdjustment":
        with DBSession() as db:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def json(self):
        return {
            "id": self.id,
            "quantity": self.quantity,
            "department": self.department.name,
            "stock": [a.json() for a in self.stock],
            "created_at": self.created_at.isoformat(),
        }
