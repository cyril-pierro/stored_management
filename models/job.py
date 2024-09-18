import datetime

import sqlalchemy as sq
from sqlalchemy import Column
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession


class Job(Base):
    __tablename__ = "jobs"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    name = Column(sq.String(200), nullable=False, unique=True)
    staff = relationship("Staff", back_populates="job")
    created_at = Column(sq.DateTime, default=datetime.datetime.now())

    def save(self, merge=False) -> "Job":
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
            "name": self.name,
        }
