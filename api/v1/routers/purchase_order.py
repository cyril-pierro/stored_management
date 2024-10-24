from fastapi import APIRouter, Depends, Query
from controllers.purchase_order import (
    PurchaseOrderController,
    PurchaseOrderItemController,
    PaymentTermsController
)
from schemas.purchase_order import (
    PurchaseOrderTypeIn,
    PurchaseOrderItemIn,
    PurchaseOrderIn,
    EditPurchaseOrderIn,
    PurchaseOrderOut,
    PurchaseOrderItemOut,
    PurchaseOrderTypeOut,
    UpdateStateIn,
    PurchaseOrderQueryIn,
    PaymentTermIn,
    PaymentTermsOut,
    EventPurchaseOrdersOut
)
from schemas.operations import SuccessOut
from controllers.auth import Auth
from controllers.operations import StaffOperator
from error import AppError
from fastapi_pagination import Page
from typing import Optional

from utils.common import bearer_schema

po_router = APIRouter()

PERMISSION_ERROR = "You do not have permission to perform this operation"


@po_router.get("/purchase-order-types", response_model=list[PurchaseOrderTypeOut])
def get_all_purchase_order_types(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        return PurchaseOrderController.get_purchase_order_types()
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.post("/purchase-order-types", response_model=PurchaseOrderTypeOut)
def create_purchase_order_type(
    data: PurchaseOrderTypeIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        return PurchaseOrderController.create_purchase_order_type(data)
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.put("/purchase-order-types/{id}", response_model=PurchaseOrderTypeOut)
def update_purchase_order_type(
    id: int, data: PurchaseOrderTypeIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        return PurchaseOrderController.update_purchase_order_type(id, data)
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.delete("/purchase-order-types/{id}", response_model=SuccessOut)
def delete_purchase_order_type(
    id: int,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        PurchaseOrderController.delete_purchase_order_type(id)
        return {"message": "Purchase order type deleted successfully"}
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.get("/purchase-orders", response_model=Page[PurchaseOrderOut])
def get_all_purchase_orders(
    q: PurchaseOrderQueryIn = Depends(),
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        return PurchaseOrderController.get_all_purchase_orders(q.__dict__)
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.get("/purchase-orders/{purchase_order_id}", response_model=PurchaseOrderOut)
def get_all_purchase_orders_by_id(
    purchase_order_id: int,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        return PurchaseOrderController.get_purchase_order_by_id(purchase_order_id)
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.post("/purchase-orders", response_model=PurchaseOrderOut)
def create_purchase_order(
    data: PurchaseOrderIn,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        return PurchaseOrderController.create_purchase_order(data)
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.put("/purchase-orders/{purchase_order_id}", response_model=PurchaseOrderOut)
def update_purchase_order(
    purchase_order_id: int,
    data: EditPurchaseOrderIn,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        return PurchaseOrderController.update_purchase_order(purchase_order_id, data)
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.delete("/purchase-orders/{purchase_order_id}", response_model=SuccessOut)
def delete_purchase_order(
    purchase_order_id: int,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        PurchaseOrderController.delete_purchase_order(purchase_order_id)
        return {"message": "Purchase order deleted successfully"}
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.post("/purchase-orders/{purchase_order_id}/update-state",
                response_model=PurchaseOrderOut
                )
def update_state_of_purchase_order(
    purchase_order_id: int,
    data: UpdateStateIn,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        return PurchaseOrderController.update_state_of_purchase_order(
            id=purchase_order_id, state=data.state, by_user_id=staff_id
        )
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.post("/purchase-order-items/{purchase_order_id}", response_model=PurchaseOrderItemOut)
def create_purchase_order_item(
    purchase_order_id: int,
    data: PurchaseOrderItemIn,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        return PurchaseOrderItemController.create_purchase_order_item(
            purchase_order_id, data
        )
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.put("/purchase-order-items/{id}", response_model=PurchaseOrderItemOut)
def update_purchase_order_item(
    id: int,
    data: PurchaseOrderItemIn,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        return PurchaseOrderItemController.update_purchase_order_item(id, data)
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.delete("/purchase-order-items/{id}", response_model=SuccessOut)
def delete_purchase_order_item(
    id: int,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        PurchaseOrderItemController.delete_purchase_order_item(id)
        return {"message": "Purchase order item deleted successfully"}
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@po_router.get("/payment-terms", response_model=list[PaymentTermsOut])
def get_all_payment_terms():
    return PaymentTermsController.get_payment_terms()


@po_router.post("/payment-terms", response_model=PaymentTermsOut)
def create_payment_term(data: PaymentTermIn):
    return PaymentTermsController.create_payment_term(data)


@po_router.put("/payment-terms/{id}", response_model=PaymentTermsOut)
def modify_payment_term(id: int, data: PaymentTermIn):
    return PaymentTermsController.edit_payment_term(id, data)


@po_router.delete("/payment-terms/{id}", response_model=SuccessOut)
def delete_payment_term(id: int):
    PaymentTermsController.delete_payment_term(id)
    return {"message": "Payment term deleted successfully"}


@po_router.get("/purchase-orders/{purchase_order_id}/generate", response_model=EventPurchaseOrdersOut)
def get_purchase_orders_details(
    purchase_order_id: int,
    prev: Optional[bool] = Query(None),
    next: Optional[bool] = Query(None),
):
    return PurchaseOrderController.get_purchase_order_by_event(
        purchase_order_id,
        next=next,
        prev=prev
    )
