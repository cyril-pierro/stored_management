import datetime

import sqlalchemy as sq
from sqlalchemy import Column
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession


class Barcode(Base):
    __tablename__ = "barcode"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    barcode = Column(sq.String, unique=True, index=True)
    code = Column(sq.String, index=True)
    specification = Column(sq.String)
    location = Column(sq.String)
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
    created_at = Column(sq.DateTime, default=datetime.datetime.now(datetime.UTC))

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
            "created_at": self.created_at.isoformat(),
        }

    @staticmethod
    def get_last_stock():
        with DBSession() as db:
            return db.query(Barcode).order_by(Barcode.id.desc()).first()
