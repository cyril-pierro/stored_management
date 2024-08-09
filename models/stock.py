import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession


class Stock(Base):
    __tablename__ = "stock"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    barcode = Column(sq.String, index=True)
    code = Column(sq.String, index=True)
    specification = Column(sq.String)
    location = Column(sq.String)
    quantity = Column(sq.Integer)
    cost = Column(sq.Float, nullable=False, default="0.0", server_default="0.0")
    created_by = Column(sq.Integer, ForeignKey("staff.id"))
    updated_by = Column(sq.Integer, ForeignKey("staff.id"))
    creator = relationship(
        "Staff", foreign_keys=[created_by], back_populates="created_stocks"
    )
    modifier = relationship(
        "Staff", foreign_keys=[updated_by], back_populates="modified_stocks"
    )
    stock_out = relationship("StockOut", back_populates="stock")
    orders = relationship("Orders", back_populates="stock")
    created_at = Column(sq.DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(sq.DateTime, default=datetime.datetime.now(datetime.UTC))

    def save(self):
        with DBSession() as db:
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
            "quantity": self.quantity,
            "cost": self.cost,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @staticmethod
    def get_last_stock():
        with DBSession() as db:
            return db.query(Stock).order_by(Stock.id.desc()).first()
