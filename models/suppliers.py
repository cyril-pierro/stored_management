import datetime

import sqlalchemy as sq
from sqlalchemy import Column
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession


class Suppliers(Base):
    __tablename__ = "suppliers"
    id = Column(sq.Integer, primary_key=True, nullable=False)
    name = Column(sq.String, nullable=False, unique=True)

    purchase_orders = relationship("PurchaseOrders", back_populates="suppliers", passive_deletes="all",
                                   passive_updates=True)

    created_at = Column(sq.DateTime, default=datetime.datetime.now())

    def save(self):
        with DBSession() as db:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }

    def update(self, data: dict) -> "Suppliers":
        with DBSession() as db:
            db.query(Suppliers).filter(
                Suppliers.id == self.id
            ).update(data)
            db.commit()
            return self

    def delete(self, force=False) -> bool:
        with DBSession() as db:
            if force:
                self = db.merge(self)
            db.delete(self)
            db.commit()
            return True
