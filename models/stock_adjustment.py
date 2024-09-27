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
    cost = Column(sq.Float, nullable=False, default=0)
    barcode_id = Column(sq.Integer, ForeignKey("barcodes.id"), nullable=False)
    department_id = Column(sq.Integer, ForeignKey("departments.id"))
    created_by = Column(sq.Integer, ForeignKey("staffs.id"))
    updated_by = Column(sq.Integer, ForeignKey("staffs.id"))
    barcode = relationship(
        "Barcode", lazy="selectin", back_populates="stock_adjustments"
    )
    department = relationship(
        "Department", lazy="selectin", back_populates="stock_adjustments"
    )
    created_at = Column(sq.DateTime, default=datetime.datetime.now())
    updated_at = Column(sq.DateTime, default=datetime.datetime.now())

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
            "department_id": self.department_id,
            "barcode": self.barcode,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
