from models.purchase_order import PurchaseOrders
from models.purchase_order_type import PurchaseOrderTypes
from models.purchase_order_items import PurchaseOrderItems
from models.payment_terms import PaymentTerms
from models.suppliers import Suppliers
from utils.session import DBSession
from utils.enum import PurchaseOrderStates
from error import AppError
from schemas.purchase_order import (
    PurchaseOrderTypeIn,
    PurchaseOrderItemIn,
    PurchaseOrderIn,
    EditPurchaseOrderIn,
    PaymentTermIn,
    SuppliersIn
)
from schemas.stock import StockIn
from controllers.stock import StockOperator
from utils.filter_sort import FilterSort
from controllers.operations import StaffOperator

MESSAGE = "Purchase order item can only be created when in draft state"


class PurchaseOrderController:
    @staticmethod
    def get_all_purchase_orders(q: dict):
        with DBSession() as db:
            q["sort"] = "-id"
            filter_data = FilterSort(PurchaseOrders, q, db)
            return filter_data.filter_and_sort()

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
                db.query(PurchaseOrderTypes).filter(
                    PurchaseOrderTypes.id == id).first()
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
            purchase_order.purchase_order_items.append(
                PurchaseOrderItems(**item))
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
    def update_state_of_purchase_order(
        id: int, state: PurchaseOrderStates, by_user_id: int
    ):
        purchase_order = PurchaseOrderController.get_purchase_order_by_id(id)
        is_manager = StaffOperator.has_manager_permission(by_user_id)
        if (
            purchase_order.state.name == PurchaseOrderStates.validated.name
            and is_manager
        ):
            if state.name != PurchaseOrderStates.canceled.name:
                raise AppError(
                    message="Purchase order has already been validated", status_code=400
                )
            for purchase_order_items in purchase_order.purchase_order_items:
                stock_id = purchase_order_items.stock_id
                purchase_order_items.stock_id = None
                purchase_order_items.save(merge=True)
                try:
                    # StockOperator.remove_stock(stock_id=stock_id)
                    StockOperator.mark_stock_as_cancelled(stock_id)
                except AppError as e:
                    purchase_order_items.stock_id = stock_id
                    purchase_order_items.save(merge=True)
                    raise AppError(message=e.message,
                                   status_code=e.status_code) from e

        if purchase_order.state.name == PurchaseOrderStates.canceled.name:
            raise AppError(
                message="Purchase order has already been canceled", status_code=400
            )
        purchase_order_done = purchase_order.update({"state": state.name})
        if (
            purchase_order_done.state.name == PurchaseOrderStates.validated.name
            and is_manager
        ):
            for purchase_order_item_data in purchase_order_done.purchase_order_items:
                stock_in_data = StockIn(
                    barcode_id=purchase_order_item_data.barcode_id,
                    quantity=purchase_order_item_data.quantity,
                    cost=purchase_order_item_data.price,
                )
                stock = StockOperator.add_stock(
                    stock_in_data, purchase_order_item_data.requested_by
                )
                purchase_order_item_data.update({"stock_id": stock.id})
        return purchase_order_done

    @staticmethod
    def delete_purchase_order(id: int):
        value = PurchaseOrderController.get_purchase_order_by_id(id)
        if value.state.name != "draft":
            raise AppError(
                message="Purchase order can only be updated when in draft state",
                status_code=400,
            )
        return value.delete(force=True)

    @staticmethod
    def get_purchase_order_by_event(
        purchase_order_by_id: int, next: bool = False, prev: bool = False
    ):
        values = {}
        with DBSession() as db:
            data = (
                db.query(PurchaseOrders)
                .filter(PurchaseOrders.id == purchase_order_by_id)
                .first()
            )
            if next:
                next_value = (
                    db.query(PurchaseOrders)
                    .filter(PurchaseOrders.id > purchase_order_by_id)
                    .order_by(PurchaseOrders.id)
                    .first()
                )
                prev_value = (
                    db.query(PurchaseOrders)
                    .filter(PurchaseOrders.id < purchase_order_by_id)
                    .order_by(PurchaseOrders.id.desc())
                    .first()
                )
                values["next"] = next_value.id if next_value else bool(
                    next_value)
                values["prev"] = prev_value.id if prev_value else bool(
                    prev_value)
            if prev:
                prev_value = (
                    db.query(PurchaseOrders)
                    .filter(PurchaseOrders.id < purchase_order_by_id)
                    .order_by(PurchaseOrders.id)
                    .first()
                )
                next_value = (
                    db.query(PurchaseOrders)
                    .filter(PurchaseOrders.id > purchase_order_by_id)
                    .order_by(PurchaseOrders.id)
                    .first()
                )
                values["prev"] = prev_value.id if prev_value else bool(
                    prev_value)
                values["next"] = next_value.id if next_value else bool(
                    next_value)
            values["current"] = data
            return values


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
                db.query(PurchaseOrderItems).filter(
                    PurchaseOrderItems.id == id).first()
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


class PaymentTermsController:
    @staticmethod
    def get_payment_terms():
        with DBSession() as db:
            return db.query(PaymentTerms).all()

    @staticmethod
    def get_payment_term_by_id(payment_term_id: int):
        with DBSession() as db:
            value = (
                db.query(PaymentTerms)
                .filter(PaymentTerms.id == payment_term_id)
                .first()
            )
            if not value:
                raise AppError(
                    message="Payment term does not exist", status_code=404)
            return value

    @staticmethod
    def create_payment_term(data: PaymentTermIn):
        payment_created = PaymentTerms(**data.model_dump())
        return payment_created.save()

    @staticmethod
    def edit_payment_term(payment_term_id: int, data: PaymentTermIn):
        payment = PaymentTermsController.get_payment_term_by_id(
            payment_term_id)
        for key, value in data.model_dump().items():
            setattr(payment, key, value)
        return payment.save(merge=True)

    @staticmethod
    def delete_payment_term(payment_term_id: int):
        payment = PaymentTermsController.get_payment_term_by_id(
            payment_term_id)
        return payment.delete(force=True)


class SupplierController:
    @staticmethod
    def create_supplier(data: SuppliersIn):
        supplier_saved = Suppliers(**data.model_dump())
        return supplier_saved.save()
    
    @staticmethod
    def get_all_suppliers():
        with DBSession() as db:
            return db.query(Suppliers).all()

    @staticmethod
    def get_supplier_by_id(supplier_id: int) -> Suppliers:
        with DBSession() as db:
            supplier_found = db.query(Suppliers).filter(
                Suppliers.id == supplier_id).first()
            if not supplier_found:
                raise AppError(message="Supplier not found", status_code=404)
            return supplier_found

    @staticmethod
    def update_supplier_by_id(supplier_id: int, data: SuppliersIn) -> Suppliers:
        found_supplier = SupplierController.get_supplier_by_id(supplier_id)
        return found_supplier.update(data.model_dump())

    @staticmethod
    def delete_supplier_by_id(supplier_id: int) -> bool:
        found_supplier = SupplierController.get_supplier_by_id(supplier_id)
        found_supplier.delete(force=True)
        return True
