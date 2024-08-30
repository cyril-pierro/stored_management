import datetime

import sqlalchemy as sq
from sqlalchemy import Column
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.enum import RolesStatus
from utils.session import DBSession


class Roles(Base):
    __tablename__ = "roles"
    id = Column(sq.Integer, primary_key=True, nullable=False)
    name = Column(
        sq.Enum(RolesStatus), nullable=False, default=RolesStatus.engineer.name
    )
    staff = relationship("Staff", back_populates="roles")
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
            "name": self.name.value,
        }
