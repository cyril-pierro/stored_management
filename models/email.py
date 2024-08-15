import datetime
from typing import Union

import sqlalchemy as sq
from pydantic import EmailStr
from sqlalchemy import Column

from core.setup import Base
from utils.session import DBSession


class Recipients(Base):
    __tablename__ = "emails"
    id = Column(sq.Integer, primary_key=True, unique=True, index=True)
    email = Column(sq.String, unique=True, index=True)
    created_at = Column(sq.DateTime, default=datetime.datetime.now(datetime.UTC))

    def save(self, merge=False) -> "Recipients":
        with DBSession() as db:
            if merge:
                self = db.merge(self)
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def json(self):
        return {"id": self.id, "email": self.email}

    @staticmethod
    def create_recipient(email: EmailStr) -> "Recipients":
        if Recipients.find_recipient(email):
            raise ValueError("Recipient email already exists")
        new_recipient = Recipients(email=email)
        return new_recipient.save()

    @staticmethod
    def find_recipient(email: Union[EmailStr, int]) -> "Recipients":
        with DBSession() as db:
            if isinstance(email, EmailStr):
                return db.query(Recipients).filter(Recipients.email == email).first()
            return db.query(Recipients).filter(Recipients.id == email).first()

    @staticmethod
    def update_recipient(recipient_id: int, email: EmailStr) -> "Recipients":
        value = Recipients.find_recipient(recipient_id)
        if not value:
            raise ValueError("Recipient does not exist")
        value.email = email
        return value.save(merge=True)

    @staticmethod
    def delete_recipient(recipient_id: int) -> bool:
        value = Recipients.find_recipient(recipient_id)
        if not value:
            raise ValueError("Recipient does not exist")
        with DBSession() as db:
            db.delete(value)
            db.commit()
            return True

    @staticmethod
    def get_all_recipients():
        with DBSession() as db:
            return db.query(Recipients).all()
