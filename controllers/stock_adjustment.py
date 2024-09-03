import datetime
from typing import Any, Union

from sqlalchemy import func

from controllers.stock import StockOperator as SO
from controllers.stock_running import StockRunningOperator as SR
from models.barcode import Barcode
from models.stock_adjustment import StockAdjustment
from schemas.stock import StockAdjustmentIn, UpdateStockAdjustmentIn, StockQuery
from utils.session import DBSession
from utils.countFilter import StockFilter


def parse_stock_adjustment_data(data: Union[Any, list, None]):
    if not data:
        return data
    if isinstance(data, list):
        return [
            {
                "id": i[0].id,
                "barcode": i[0].barcode,
                "location": i[0].location,
                "specification": i[0].specification,
                "code": i[0].code,
                # "cost": i[0].cost,
                "quantity": i[1],
                "department_id": i[2],
            }
            for i in data
        ]
    return {
        "id": data[0].id,
        "barcode": data[0].barcode,
        "location": data[0].location,
        "specification": data[0].specification,
        "code": data[0].code,
        # "cost": data[0].cost,
        "quantity": data[1],
        "department_id": data[2],
    }


class StockAdjustmentOperator:
    @staticmethod
    def get_all_stock_adjustments():
        with DBSession() as db:
            data = db.query(StockAdjustment).order_by(
                StockAdjustment.id.desc()).all()
        return data

    @staticmethod
    def create_stock_adjustment(barcode: str, data: StockAdjustmentIn, staff_id: int):
        stock = SO.get_grouped_stocks_with_stock_barcode(barcode)

        if not stock:
            raise ValueError("Stock not found to perform stock adjustment")

        running_stock = SR.get_stock_in_inventory(barcode)

        if data.quantity > running_stock.remaining_quantity:
            raise ValueError(
                "Stock adjustment Entry error. Quantity entered is more than Stock available quantity"
            )
        values = data.__dict__
        values["created_by"] = staff_id
        barcode_found = SO.get_barcode(barcode)
        values["barcode_id"] = barcode_found.id
        stock_adj = StockAdjustment(**values)
        value = stock_adj.save()
        grouped_data: dict[str, Any] = (
            StockAdjustmentOperator.get_grouped_stock_adjustments_by_barcode(
                barcode)
        )
        SR.create_running_stock(
            barcode,
            stock_operator=SO,
            adjustment_quantity=grouped_data.get("quantity"),
            order_quantity=data.quantity,
        )
        return value

    @staticmethod
    def update_stock_adjustment(id: int, data: UpdateStockAdjustmentIn, staff_id: int):
        with DBSession() as db:
            stock_adj_found = (
                db.query(StockAdjustment).filter(
                    StockAdjustment.id == id).first()
            )
            if not stock_adj_found:
                raise ValueError("Stock Adjustment record not found")
            stock_adj_found.department_id = data.department_id
            stock_adj_found.quantity = data.quantity
            stock_adj_found.updated_at = datetime.datetime.now()
            stock_adj_found.updated_by = staff_id
            stock_adj_found.updated_at = datetime.datetime.now()
            db.add(stock_adj_found)
            db.commit()
            db.refresh(stock_adj_found)
        grouped_data: dict[str, Any] = (
            StockAdjustmentOperator.get_grouped_stock_adjustments_by_barcode(
                stock_adj_found.barcode.barcode
            )
        )
        SR.create_running_stock(
            stock_adj_found.barcode.barcode,
            stock_operator=SO,
            adjustment_quantity=grouped_data.get("quantity"),
        )
        return stock_adj_found

    @staticmethod
    def delete_stock_adjustment(id: int):
        with DBSession() as db:
            stock_adj_found = (
                db.query(StockAdjustment).filter(
                    StockAdjustment.id == id).first()
            )
            if not stock_adj_found:
                raise ValueError("Stock Adjustment record not found")
            barcode = stock_adj_found.barcode.barcode
            db.delete(stock_adj_found)
            db.commit()
        grouped_data: dict[str, Any] = (
            StockAdjustmentOperator.get_grouped_stock_adjustments_by_barcode(
                barcode
            )
        )
        SR.create_running_stock(
            stock_adj_found.barcode.barcode,
            stock_operator=SO,
            adjustment_quantity=(
                -1 if not grouped_data else grouped_data.get("quantity", 0)
            ),
        )
        return True

    @staticmethod
    def group_all_stock_adjustments_for_stocks(query_params: StockQuery):
        with DBSession() as db:
            query = (
                db.query(
                    Barcode,
                    func.sum(StockAdjustment.quantity).label("total_quantity"),
                    StockAdjustment.department_id,
                )
                .join(
                    StockAdjustment, Barcode.id == StockAdjustment.barcode_id
                )
                .group_by(StockAdjustment.barcode_id, Barcode.id, StockAdjustment.department_id)
            )
        filter_instance = StockFilter(query_params, query_to_use=query)
        return parse_stock_adjustment_data(filter_instance.apply())

    @staticmethod
    def get_grouped_stock_adjustments_by_barcode(barcode: str):
        with DBSession() as db:
            query = (
                db.query(
                    Barcode,
                    func.sum(StockAdjustment.quantity).label("total_quantity"),
                    StockAdjustment.department_id,
                )
                .join(StockAdjustment, Barcode.id == StockAdjustment.barcode_id)
                .filter(Barcode.barcode == barcode)
                .group_by(StockAdjustment.barcode_id, Barcode.id, StockAdjustment.department_id)
            )
        return parse_stock_adjustment_data(query.one_or_none())
