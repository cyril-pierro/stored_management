import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession


class Stock(Base):
    __tablename__ = "stock"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    barcode_id = Column(sq.Integer, ForeignKey("barcode.id"), nullable=False)
    quantity = Column(sq.Integer, default=0)
    quantity_initiated = Column(sq.Integer, nullable=False, default=0, server_default=0)
    sold = Column(sq.Boolean, default=False)
    cost_id = Column(sq.Integer, ForeignKey("costs.id"), nullable=False)
    created_by = Column(sq.Integer, ForeignKey("staff.id"))
    updated_by = Column(sq.Integer, ForeignKey("staff.id"))
    costs = relationship(
        "Costs",
        lazy="selectin",
        back_populates="stock",
        passive_deletes="all",
        passive_updates=True,
    )
    creator = relationship(
        "Staff",
        foreign_keys=[created_by],
        back_populates="created_stocks",
        lazy="subquery",
    )
    modifier = relationship(
        "Staff",
        foreign_keys=[updated_by],
        back_populates="modified_stocks",
        lazy="subquery",
    )
    barcode = relationship("Barcode", back_populates="stock", lazy="subquery")
    sold_at = Column(sq.DateTime)
    created_at = Column(sq.DateTime, default=datetime.datetime.now())
    updated_at = Column(sq.DateTime)

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
            "sold": self.sold,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at.isoformat(),
            # "updated_at": self.updated_at.isoformat(),
        }
