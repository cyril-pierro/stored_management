import datetime
from typing import Any

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.enum import OrderStatus
from utils.session import DBSession


class Orders(Base):
    __tablename__ = "orders"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    staff_id = Column(sq.Integer, ForeignKey("staff.id"))
    barcode_id = Column(sq.Integer, ForeignKey("barcode.id"), nullable=False)
    part_name = Column(sq.String, nullable=True)
    job_number = Column(sq.String, nullable=False)
    quantity = Column(sq.Integer)
    available_quantity = Column(sq.Integer, default=0)
    restrictions = Column(
        sq.Enum(OrderStatus), nullable=False, default=OrderStatus.part_available.name
    )
    barcode = relationship("Barcode", back_populates="orders")
    stock_out = relationship("StockOut", back_populates="orders")
    staff = relationship(
        "Staff", foreign_keys=[staff_id], back_populates="orders", lazy="selectin"
    )
    created_at = Column(sq.DateTime, default=datetime.datetime.now())

    def save(self) -> "Orders":
        with DBSession() as db:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def json(self) -> dict[str, Any]:
        return {
            "id": f"#-{self.id}",
            "staff": self.staff.name,
            "barcode": self.barcode.json(),
            "job_number": self.job_number,
            "part_name": self.part_name,
            "quantity": self.quantity,
            "restrictions": self.restrictions.value,
            "created_at": self.created_at.isoformat(),
            # "updated_at": self.created_at.isoformat(),
        }
    
    def erm_report(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "date": self.created_at.isoformat(),
            "event_number": self.job_number or 0,
            "part_code": self.barcode.barcode,
            "part_type": self.part_name,
            "part_description": self.barcode.specification,
            "quantity": self.quantity,
            "erm_code": self.barcode.stock[0].erm_code,
        }
# Stock.erm_code.is_not(None)