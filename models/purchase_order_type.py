import datetime

import sqlalchemy as sq
from sqlalchemy import Column

from core.setup import Base
from utils.session import DBSession


class PurchaseOrderTypes(Base):
    __tablename__ = "purchase_order_types"
    id = Column(sq.Integer, primary_key=True, unique=True, nullable=False)
    name = Column(sq.String, nullable=False)

    created_at = Column(sq.DateTime, default=datetime.datetime.now())

    def save(self, merge=False) -> "PurchaseOrderTypes":
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
            "created_at": self.created_at.isoformat(),
        }
