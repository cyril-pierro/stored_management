from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional
from utils.enum import PurchaseOrderStates


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
    supplier_code: str
    quantity: int
    price: float
    sub_total: float
    requested_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseOrderIn(BaseModel):
    supplier_name: str
    payment_terms: str
    order_type_id: int
    purchase_order_items: list[PurchaseOrderItemIn]


class EditPurchaseOrderIn(BaseModel):
    supplier_name: str
    payment_terms: str
    order_type_id: int


class PurchaseOrderOut(PurchaseOrderIn):
    id: int
    supplier_name: str
    payment_terms: str
    state: PurchaseOrderStates
    order_type_id: int
    purchase_order_items: list[PurchaseOrderItemOut]
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateStateIn(BaseModel):
    state: PurchaseOrderStates