from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional, Union
from utils.enum import PurchaseOrderStates
from fastapi import Query


class BarcodeOut(BaseModel):
    barcode: str
    code: str
    specification: str
    location: str
    erm_code: Optional[str] = None

    class Config:
        from_attributes = True


class RequestedByOut(BaseModel):
    name: str

    class Config:
        from_attributes = True


class PurchaseOrderTypeIn(BaseModel):
    name: str


class PurchaseOrderTypeOut(PurchaseOrderTypeIn):
    id: int
    name: str

    class Config:
        from_attributes = True


class PurchaseOrderItemIn(BaseModel):
    barcode_id: int
    supplier_code: str
    quantity: int
    price: float
    requested_by: int
    sub_total: Optional[float] = 0.0

    @model_validator(mode="after")
    def _compute_sub_total(self) -> "PurchaseOrderItemIn":
        self.sub_total = self.quantity * self.price
        return self


class PurchaseOrderItemOut(PurchaseOrderItemIn):
    id: int
    barcode_id: int
    barcode: BarcodeOut
    supplier_code: str
    quantity: int
    price: float
    sub_total: float
    requested_by: int
    requested_by_staff: RequestedByOut
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseOrderIn(BaseModel):
    supplier_name: str
    payment_term_id: int
    order_type_id: int
    purchase_order_items: list[PurchaseOrderItemIn]


class PurchaseOrderQueryIn(BaseModel):
    supplier_name: Union[str, None] = Query(default=None)
    created_at_max: Union[str, None] = Query(default=None)
    created_at_min:  Union[str, None] = Query(default=None)
    state:  Union[PurchaseOrderStates, None] = Query(default=None)


class PaymentTermIn(BaseModel):
    name: str
    num_of_days: int


class PaymentTermsOut(BaseModel):
    id: int
    name: str
    num_of_days: int

    class Config:
        from_attributes = True


class EditPurchaseOrderIn(BaseModel):
    supplier_name: str
    payment_term_id: int
    order_type_id: int


class PurchaseOrderOut(PurchaseOrderIn):
    id: int
    supplier_name: str
    payment_terms: PaymentTermsOut
    state: PurchaseOrderStates
    order_type_id: int
    purchase_order_items: list[PurchaseOrderItemOut]
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateStateIn(BaseModel):
    state: PurchaseOrderStates


class EventPurchaseOrdersOut(BaseModel):
    prev: Optional[Union[PurchaseOrderOut, bool, None, int]] = None
    next: Optional[Union[PurchaseOrderOut, bool, None, int]] = None
    current: Optional[Union[PurchaseOrderOut, bool, None, int]] = None