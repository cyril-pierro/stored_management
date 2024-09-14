from pydantic import BaseModel, EmailStr

from utils.enum import RolesStatus
from datetime import datetime


class SuccessOut(BaseModel):
    message: str


class CategoryIn(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: int
    name: str
    created_at: datetime


class JobIn(BaseModel):
    name: str


class JobOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class DepartmentIn(JobIn):
    pass


class DepartmentOut(JobOut):
    pass


class RolesOut(BaseModel):
    id: int
    name: RolesStatus

    class Config:
        from_attributes = True


class EmailConfigureIn(BaseModel):
    email: EmailStr


class EmailConfigureOut(EmailConfigureIn):
    id: int
