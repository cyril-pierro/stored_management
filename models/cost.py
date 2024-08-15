import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession


class Costs(Base):
    __tablename__ = "costs"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    cost = Column(sq.Float, unique=True, nullable=False, default=0.0)
    created_at = Column(sq.DateTime, default=datetime.datetime.now(datetime.UTC))
    stock = relationship("Stock", back_populates="costs")

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
            "cost": self.cost,
            "sold": self.sold,
        }
