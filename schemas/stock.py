from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from utils.enum import OrderStatus, RunningStockStatus


class CostOut(BaseModel):
    id: int
    cost: float
    created_at: datetime


class Barcode(BaseModel):
    id: Optional[int]
    barcode: str
    code: str
    specification: str
    location: str
    prices: Optional[set[str]] = None
    quantity: Optional[int] = None

    class Config:
        from_attributes = True


class Order(BaseModel):
    id: int
    staff_id: int
    barcode: Barcode
    job_number: str
    quantity: int
    restrictions: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True


class StockIn(BaseModel):
    barcode: str
    specification: str
    location: str
    quantity: int
    cost: float


class StockOut(BaseModel):
    id: int
    quantity: int
    sold: bool
    barcode: Barcode
    costs: CostOut
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockAdjustmentIn(BaseModel):
    department_id: int
    quantity: int


class UpdateStockAdjustmentIn(StockAdjustmentIn):
    barcode: str


class StockAdjustmentOut(StockAdjustmentIn):
    id: int
    barcode: Barcode
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockAdjustmentGroupOut(Barcode):
    department_id: int


class StockOutIn(BaseModel):
    quantity: int
    # barcode: str


class StockOutOut(BaseModel):
    id: int
    quantity: int
    barcode: Barcode
    orders: Optional[Order]
    created_at: datetime


class RunningStockOut(BaseModel):
    id: int
    status: RunningStockStatus
    stock_quantity: int
    out_quantity: int
    adjustment_quantity: int
    remaining_quantity: int
    barcode: Barcode
    created_at: datetime


class RunningStockAvailabilityOut(BaseModel):
    barcode: str
    specification: str
    location: str
    available: RunningStockStatus
    running_stock: int
