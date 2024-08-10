import datetime

import sqlalchemy as sq
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from models.department import Department
from models.job import Job
from models.order import Orders
from models.stock import Stock
from utils.session import DBSession


class Staff(Base):
    __tablename__ = "staff"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    name = Column(sq.String, nullable=False)
    staff_id_number = Column(sq.String, nullable=False, unique=True, index=True)
    job_id = Column(sq.Integer, ForeignKey("job.id"), nullable=False)
    department_id = Column(sq.Integer, ForeignKey("department.id"), nullable=False)
    job = relationship(Job, back_populates="staff")
    department = relationship(Department, back_populates="staff")
    created_stocks = relationship(
        "Stock", foreign_keys=[Stock.created_by], back_populates="creator"
    )
    modified_stocks = relationship(
        "Stock", foreign_keys=[Stock.updated_by], back_populates="modifier"
    )
    orders = relationship(Orders, back_populates="staff")
    created_at = Column(sq.DateTime, default=datetime.datetime.now(datetime.UTC))

    def save(self) -> "Staff":
        with DBSession() as db:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "job_title": self.job.name,
            "department": self.department.name,
        }
