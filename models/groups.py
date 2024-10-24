import datetime

import sqlalchemy as sq
from sqlalchemy import Column
from utils.enum import GroupStates

from core.setup import Base
from utils.session import DBSession
from sqlalchemy.orm import relationship
from models.staff import Staff


class Groups(Base):
    __tablename__ = "groups"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    group = Column(sq.Enum(GroupStates), default=GroupStates.users.name)

    staffs = relationship(Staff, back_populates="groups")
    created_at = Column(sq.DateTime, default=datetime.datetime.now())

    def _save_to_db(self, merge=False):
        with DBSession() as db:
            if merge:
                self = db.merge(self)
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def save(self, merge=False) -> "Groups":
        self._save_to_db(merge)

    def json(self):
        return {"id": self.id, "group": self.group.name}

    def update(self, data: dict, merge=False) -> "Groups":
        for key, value in data.items():
            setattr(self, key, value)
        return self._save_to_db(merge)

    def delete(self, force=False):
        with DBSession() as db:
            if force:
                self = db.merge(self)
            db.delete(self)
            db.commit()
            return True
