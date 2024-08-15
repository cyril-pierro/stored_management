from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.staff import StaffOut
from schemas.stock import Barcode
from utils.enum import OrderStatus


class OrderIn(BaseModel):
    job_number: str
    part_name: Optional[str]
    quantity: int


class OrderOut(BaseModel):
    id: int
    job_number: str
    staff: StaffOut
    quantity: int
    restrictions: OrderStatus
    barcode: Barcode
    available_quantity: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrdersDoneOut(BaseModel):
    number: int
