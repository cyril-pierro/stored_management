import datetime

import sqlalchemy as sq
from sqlalchemy import Column
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession


class Department(Base):
    __tablename__ = "department"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    name = Column(sq.String(200), nullable=False, unique=True)
    staff = relationship("Staff", back_populates="department")
    created_at = Column(sq.DateTime, default=datetime.datetime.now(datetime.UTC))

    def save(self) -> "Department":
        with DBSession() as db:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
        }
