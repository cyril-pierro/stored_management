from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel
from fastapi import Query

from schemas.staff import StaffOut
from utils.enum import OrderStatus, RunningStockStatus


class CostOut(BaseModel):
    id: int
    cost: float
    created_at: datetime


class BarcodeIn(BaseModel):
    barcode: str
    specification: str
    location: str
    category: str

    class Config:
        from_attributes = True


class UpdateIn(BaseModel):
    barcode: str
    specification: str
    location: str

    class Config:
        from_attributes = True


class Barcode(BaseModel):
    id: Optional[int]
    barcode: str
    code: str
    specification: str
    location: str
    created_at: Optional[datetime] = None
    prices: Optional[set[Union[float, str]]] = None
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
    barcode_id: int
    quantity: int
    cost: float
    erm_code: Optional[str] = None


class StockOut(BaseModel):
    id: int
    quantity: int
    sold: bool
    barcode: Barcode
    erm_code: Optional[str] = None
    costs: CostOut
    creator: Optional[StaffOut] = None
    modifier: Optional[StaffOut] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockAdjustmentIn(BaseModel):
    department_id: int
    quantity: int


class UpdateStockAdjustmentIn(StockAdjustmentIn):
    pass


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


class CostEvaluationOut(BaseModel):
    barcode: Barcode
    quantity: int
    cost: float
    total: float
    created_at: datetime


class StockQuery(BaseModel):
    from_value: Optional[int] | None = Query(None)
    to_value: Optional[int] | None = Query(None)
    sorted: Optional[bool] | None = Query(None)