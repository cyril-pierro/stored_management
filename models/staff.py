import datetime

import sqlalchemy as sq
from passlib.context import CryptContext
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from core.setup import Base
from models.department import Department
from models.job import Job
from models.order import Orders
from models.roles import Roles
from models.stock import Stock
from utils.session import DBSession

context = CryptContext(["bcrypt"], deprecated="auto")


class Staff(Base):
    __tablename__ = "staffs"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    name = Column(sq.String, nullable=False)
    staff_id_number = Column(sq.String, nullable=False, unique=True, index=True)
    hash_password = Column(sq.String, nullable=False)

    job_id = Column(sq.Integer, ForeignKey("jobs.id"), nullable=False)
    department_id = Column(sq.Integer, ForeignKey("departments.id"), nullable=False)
    role_id = Column(sq.Integer, ForeignKey("roles.id"), nullable=False)
    group_id = Column(sq.Integer, ForeignKey("groups.id"))

    job = relationship(Job, back_populates="staff", lazy="subquery")
    groups = relationship("Groups", back_populates="staffs", lazy="subquery")
    department = relationship(Department, back_populates="staff", lazy="subquery")
    created_stocks = relationship(
        "Stock",
        foreign_keys=[Stock.created_by],
        back_populates="creator",
        lazy="subquery",
    )
    modified_stocks = relationship(
        "Stock",
        foreign_keys=[Stock.updated_by],
        back_populates="modifier",
        lazy="subquery",
    )
    orders = relationship(Orders, back_populates="staff", lazy="subquery")
    roles = relationship(Roles, back_populates="staff", lazy="subquery")
    purchase_order_items = relationship(
        "PurchaseOrderItems",
        back_populates="requested_by_staff",
        lazy="selectin",
        passive_deletes="all",
        passive_updates=True,
    )
    created_at = Column(sq.DateTime, default=datetime.datetime.now())

    def save(self, merge=False) -> "Staff":
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
            "job_title": self.job.name,
            "department": self.department.name,
            "role": self.roles.name,
        }

    @staticmethod
    def generate_hash_password(password: str) -> str:
        return context.hash(password)

    @staticmethod
    def verify_hash_password(hash_password: str, password: str) -> bool:
        try:
            return context.verify(hash=hash_password, secret=password)
        except Exception as e:
            print("Verification failed", e)
