from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, field_validator
from fastapi import Query

from schemas.staff import StaffOut
from utils.enum import OrderStatus, RunningStockStatus


class BarcodeIn(BaseModel):
    barcode: str
    specification: str
    location: str
    category: str
    erm_code: Optional[str] = None
    
    @field_validator("erm_code")
    @classmethod
    def uppercase_erm_code(cls, erm_code: str):
        return erm_code.upper() if erm_code else erm_code

    class Config:
        from_attributes = True


class UpdateIn(BaseModel):
    barcode: str
    specification: str
    location: str
    erm_code: Optional[str] = None

    class Config:
        from_attributes = True


class Barcode(BaseModel):
    id: Optional[int]
    barcode: str
    code: str
    specification: str
    location: str
    erm_code: Optional[str] = None
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


class StockOut(BaseModel):
    id: int
    quantity: int
    quantity_initiated: int
    sold: bool
    barcode: Barcode
    cost: float
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


class StockOutOut(BaseModel):
    id: int
    quantity: int
    cost: float
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
    cost: float
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
    from_value: Union[Optional[int], None] = Query(None)
    to_value: Union[Optional[int],None] = Query(None)
    sorted: Union[Optional[bool], None] = Query(None)