import datetime

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
    stock_id = Column(sq.Integer, ForeignKey("stock.id"))
    job_number = Column(sq.String, nullable=False)
    quantity = Column(sq.Integer)
    restrictions = Column(
        sq.Enum(OrderStatus), nullable=False, default=OrderStatus.part_available.name
    )
    staff = relationship("Staff", foreign_keys=[staff_id], back_populates="orders")
    stock = relationship("Stock", foreign_keys=[stock_id], back_populates="orders")
    created_at = Column(sq.DateTime, default=datetime.datetime.now(datetime.UTC))

    def save(self) -> "Orders":
        with DBSession() as db:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def json(self):
        return {
            "id": f"#-{self.id}",
            "staff": self.staff.name,
            "job_number": self.job_number,
            "quantity": self.quantity,
            "restrictions": self.restrictions.value,
            "created_at": self.created_at.isoformat(),
        }
