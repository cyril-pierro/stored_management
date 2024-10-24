import datetime

import sqlalchemy as sq
from sqlalchemy.orm import relationship
from sqlalchemy import Column

from core.setup import Base
from utils.session import DBSession


class PaymentTerms(Base):
    __tablename__ = "payment_terms"
    id = Column(sq.Integer, primary_key=True, unique=True, nullable=False)
    name = Column(sq.String, nullable=False)
    num_of_days = Column(sq.Integer)

    purchase_orders = relationship(
        "PurchaseOrders",
        back_populates="payment_terms",
        lazy="selectin",
    )

    created_at = Column(sq.DateTime, default=datetime.datetime.now())

    def save(self, merge=False) -> "PaymentTerms":
        with DBSession() as db:
            if merge:
                self = db.merge(self)
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def delete(self, force=False) -> bool:
        with DBSession() as db:
            if force:
                self = db.merge(self)
            db.delete(self)
            db.commit()
            return True

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "num_of_days": self.num_of_days,
            "created_at": self.created_at.isoformat(),
        }
