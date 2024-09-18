import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession


class CostEvaluation(Base):
    __tablename__ = "cost_evaluation"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    barcode_id = Column(sq.Integer, ForeignKey("barcodes.id"))
    quantity = Column(sq.Integer)
    cost = Column(sq.Float)
    total = Column(sq.Float)
    created_at = Column(sq.DateTime, default=datetime.datetime.now())
    barcode = relationship("Barcode", back_populates="cost_evaluation", lazy="selectin")

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
            "barcode": self.barcode.barcode,
            "specification": self.barcode.specification,
            "quantity": self.quantity,
            "cost": self.cost,
            "total": self.total,
            "created_at": self.created_at.isoformat()
        }
