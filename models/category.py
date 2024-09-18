import datetime

import sqlalchemy as sq
from sqlalchemy import Column
from sqlalchemy.orm import relationship

from core.setup import Base
from utils.session import DBSession
from schemas.operations import CategoryIn
from error import AppError
from typing import Union


class Category(Base):
    __tablename__ = "categories"
    id = Column(sq.Integer, primary_key=True,
                unique=True, index=True, nullable=False)
    name = Column(sq.String, unique=True, index=True, nullable=False)
    created_at = Column(sq.DateTime, default=datetime.datetime.now())
    barcode = relationship(
        "Barcode", back_populates="category", lazy="subquery")

    def save(self, merge=False) -> "Category":
        with DBSession() as db:
            if merge:
                self = db.merge(self)
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def remove(self, merge: bool = False):
        with DBSession() as db:
            if merge:
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

    @staticmethod
    def add(data: CategoryIn) -> "Category":
        new_category = Category(name=data.name.lower())
        return new_category.save()

    @staticmethod
    def get(category_id: Union[int, str]) -> Union[None, "Category"]:
        with DBSession() as db:
            if isinstance(category_id, int):
                return db.query(Category).filter(Category.id == category_id).first()
            return db.query(Category).filter(Category.name == category_id).first()

    @staticmethod
    def update(id: int, data: CategoryIn) -> "Category":
        found_category = Category.get(id)
        if not found_category:
            raise AppError(message="Category not found", status_code=404)
        found_category.name = data.name
        return found_category.save(merge=True)

    @staticmethod
    def get_all():
        with DBSession() as db:
            return db.query(Category).all()
