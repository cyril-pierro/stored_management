from models.purchase_order import PurchaseOrders
from models.purchase_order_type import PurchaseOrderTypes
from models.purchase_order_items import PurchaseOrderItems
from utils.session import DBSession
from utils.enum import PurchaseOrderStates
from error import AppError
from schemas.purchase_order import (
    PurchaseOrderTypeIn,
    PurchaseOrderItemIn,
    PurchaseOrderIn,
    EditPurchaseOrderIn,
)

MESSAGE = "Purchase order item can only be created when in draft state"


class PurchaseOrderController:
    @staticmethod
    def get_all_purchase_orders():
        with DBSession() as db:
            return db.query(PurchaseOrders).all()

    @staticmethod
    def get_purchase_order_types():
        with DBSession() as db:
            return db.query(PurchaseOrderTypes).all()

    @staticmethod
    def get_purchase_order_by_id(purchase_order_id: int) -> PurchaseOrders:
        with DBSession() as db:
            value = (
                db.query(PurchaseOrders)
                .filter(PurchaseOrders.id == purchase_order_id)
                .first()
            )
            if not value:
                raise AppError(
                    message=f"Purchase order with id {purchase_order_id} not found",
                    status_code=404,
                )
            return value

    @staticmethod
    def get_purchase_order_type_by_id(id: int) -> PurchaseOrderTypes:
        with DBSession() as db:
            value = (
                db.query(PurchaseOrderTypes).filter(PurchaseOrderTypes.id == id).first()
            )
            if not value:
                raise AppError(
                    message=f"Purchase order type with id {id} not found",
                    status_code=404,
                )
            return value

    @staticmethod
    def create_purchase_order_type(data: PurchaseOrderTypeIn) -> PurchaseOrderTypes:
        value = PurchaseOrderTypes(**data.model_dump())
        return value.save()

    @staticmethod
    def update_purchase_order_type(id: int, data: PurchaseOrderTypeIn):
        value = PurchaseOrderController.get_purchase_order_type_by_id(id)
        value.name = data.name
        value.save(merge=True)
        return value

    @staticmethod
    def delete_purchase_order_type(id: int):
        value = PurchaseOrderController.get_purchase_order_type_by_id(id)
        return value.delete(force=True)

    @staticmethod
    def create_purchase_order(data: PurchaseOrderIn):
        saved_data = data.model_dump()
        purchase_order_items = saved_data.pop("purchase_order_items")
        purchase_order = PurchaseOrders(**saved_data)
        for item in purchase_order_items:
            purchase_order.purchase_order_items.append(PurchaseOrderItems(**item))
        return purchase_order.save()

    @staticmethod
    def update_purchase_order(id: int, data: EditPurchaseOrderIn):
        purchase_order = PurchaseOrderController.get_purchase_order_by_id(id)
        if purchase_order.state.name != "draft":
            raise AppError(
                message="Purchase order can only be updated when in draft state",
                status_code=400,
            )
        for key, value in data.model_dump().items():
            setattr(purchase_order, key, value)
        return purchase_order.save(merge=True)

    @staticmethod
    def update_state_of_purchase_order(id: int, state: PurchaseOrderStates):
        purchase_order = PurchaseOrderController.get_purchase_order_by_id(id)
        purchase_order.state = state.name
        return purchase_order.save(merge=True)

    @staticmethod
    def delete_purchase_order(id: int):
        value = PurchaseOrderController.get_purchase_order_by_id(id)
        if value.state.name != "draft":
            raise AppError(
                message="Purchase order can only be updated when in draft state",
                status_code=400,
            )
        return value.delete(force=True)


class PurchaseOrderItemController:
    @staticmethod
    def create_purchase_order_item(purchase_order_id: int, data: PurchaseOrderItemIn):
        values = data.model_dump()
        values["purchase_order_id"] = purchase_order_id
        purchase_order = PurchaseOrderController.get_purchase_order_by_id(
            purchase_order_id
        )
        if purchase_order.state.name != "draft":
            raise AppError(
                message=MESSAGE,
                status_code=400,
            )
        value = PurchaseOrderItems(**values)
        return value.save()

    @staticmethod
    def get_purchase_order_item_by_id(id: int):
        with DBSession() as db:
            value = (
                db.query(PurchaseOrderItems).filter(PurchaseOrderItems.id == id).first()
            )
            if not value:
                raise AppError(
                    message=f"Purchase order item with id {id} not found",
                    status_code=404,
                )
            return value

    @staticmethod
    def get_all_purchase_order_items():
        with DBSession() as db:
            return db.query(PurchaseOrderItems).all()

    @staticmethod
    def update_purchase_order_item(id: int, data: PurchaseOrderItemIn):
        purchase_order_item = PurchaseOrderItemController.get_purchase_order_item_by_id(
            id
        )
        purchase_order = PurchaseOrderController.get_purchase_order_by_id(
            purchase_order_item.purchase_order_id
        )
        if purchase_order.state.name != "draft":
            raise AppError(
                message=MESSAGE,
                status_code=400,
            )

        for key, value in data.model_dump().items():
            setattr(purchase_order_item, key, value)
        return purchase_order_item.save(merge=True)

    @staticmethod
    def delete_purchase_order_item(id: int):
        value = PurchaseOrderItemController.get_purchase_order_item_by_id(id)
        purchase_order = PurchaseOrderController.get_purchase_order_by_id(
            value.purchase_order_id
        )
        if purchase_order.state.name != "draft":
            raise AppError(
                message=MESSAGE,
                status_code=400,
            )
        return value.delete(force=True)
