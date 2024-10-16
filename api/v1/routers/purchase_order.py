from fastapi import APIRouter, Depends
from controllers.purchase_order import (
    PurchaseOrderController,
    PurchaseOrderItemController,
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
)
from schemas.operations import SuccessOut


from utils.common import bearer_schema

po_router = APIRouter()


@po_router.get("/purchase-order-types", response_model=list[PurchaseOrderTypeOut])
def get_all_purchase_order_types():
    return PurchaseOrderController.get_purchase_order_types()


@po_router.post("/purchase-order-types", response_model=PurchaseOrderTypeOut)
def create_purchase_order_type(data: PurchaseOrderTypeIn):
    return PurchaseOrderController.create_purchase_order_type(data)


@po_router.put("/purchase-order-types/{id}", response_model=PurchaseOrderTypeOut)
def update_purchase_order_type(id: int, data: PurchaseOrderTypeIn):
    return PurchaseOrderController.update_purchase_order_type(id, data)


@po_router.delete("/purchase-order-types/{id}", response_model=SuccessOut)
def delete_purchase_order_type(id: int):
    PurchaseOrderController.delete_purchase_order_type(id)
    return {"message": "Purchase order type deleted successfully"}


@po_router.get("/purchase-orders", response_model=list[PurchaseOrderOut])
def get_all_purchase_orders():
    return PurchaseOrderController.get_all_purchase_orders()


@po_router.post("/purchase-orders", response_model=PurchaseOrderOut)
def create_purchase_order(data: PurchaseOrderIn):
    return PurchaseOrderController.create_purchase_order(data)


@po_router.put("/purchase-orders/{purchase_order_id}", response_model=PurchaseOrderOut)
def update_purchase_order(purchase_order_id: int, data: EditPurchaseOrderIn):
    return PurchaseOrderController.update_purchase_order(purchase_order_id, data)


@po_router.delete("/purchase-orders/{purchase_order_id}", response_model=SuccessOut)
def delete_purchase_order(purchase_order_id: int):
    PurchaseOrderController.delete_purchase_order(purchase_order_id)
    return {"message": "Purchase order deleted successfully"}


@po_router.post("/purchase-orders/{purchase_order_id}/update-state")
def update_state_of_purchase_order(purchase_order_id: int, data: UpdateStateIn):
    return PurchaseOrderController.update_state_of_purchase_order(
        purchase_order_id, data.state
    )


@po_router.post("/purchase-order-items/{purchase_order_id}")
def create_purchase_order_item(purchase_order_id: int, data: PurchaseOrderItemIn):
    return PurchaseOrderItemController.create_purchase_order_item(
        purchase_order_id, data
    )


@po_router.put("/purchase-order-items/{id}", response_model=PurchaseOrderItemOut)
def update_purchase_order_item(id: int, data: PurchaseOrderItemIn):
    return PurchaseOrderItemController.update_purchase_order_item(id, data)


@po_router.delete("/purchase-order-items/{id}", response_model=SuccessOut)
def delete_purchase_order_item(id: int):
    PurchaseOrderItemController.delete_purchase_order_item(id)
    return {"message": "Purchase order item deleted successfully"}
