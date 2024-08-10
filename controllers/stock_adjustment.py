import datetime
from typing import Any, Union

from sqlalchemy import func

from controllers.stock import StockOperator as SO
from controllers.stock_running import StockRunningOperator as SR
from models.stock_adjustment import StockAdjustment
from schemas.stock import StockAdjustmentIn, UpdateStockAdjustmentIn
from utils.session import DBSession


def parse_stock_adjustment_data(data: Union[Any, list, None]):
    if not data:
        return data
    if isinstance(data, list):
        return [
            {
                "barcode": i[0],
                "quantity": i[1],
                "deparment_id": i[2],
            }
            for i in data
        ]
    return {
        "barcode": data[0],
        "quantity": data[1],
        "deparment_id": data[2],
    }


class StockAdjustmentOperator:
    @staticmethod
    def get_all_stock_adjustments():
        with DBSession() as db:
            return db.query(StockAdjustment).all()

    @staticmethod
    def create_stock_adjustment(barcode: str, data: StockAdjustmentIn):
        stock = SO.get_grouped_stocks_with_stock_barcode(barcode)

        if not stock:
            raise ValueError("Stock not found to perform stock adjustment")

        if data.quantity >= stock.get("quantity"):
            raise ValueError(
                "Stock adjustment Entry error. Quantity entered is more than or equal to the quantity in store"
            )
        values = data.__dict__
        values["barcode"] = barcode
        stock_adj = StockAdjustment(**values)
        value = stock_adj.save()
        grouped_data: dict[
            str, Any
        ] = StockAdjustmentOperator.get_grouped_stock_adjustments_by_barcode(barcode)
        SR.create_running_stock(
            barcode, stock_operator=SO, adjustment_quantity=grouped_data.get("quantity")
        )
        return value

    @staticmethod
    def update_stock_adjustment(id: int, data: UpdateStockAdjustmentIn):
        values = data.__dict__
        values["updated_at"] = datetime.datetime.now(datetime.UTC)
        with DBSession() as db:
            stock_adj_found = (
                db.query(StockAdjustment).filter(StockAdjustment.id == id).first()
            )
            if not stock_adj_found:
                raise ValueError("Stock Adjustment record not found")
            stock_adj_found.department_id = data.department_id
            stock_adj_found.barcode = data.barcode
            stock_adj_found.quantity = data.quantity
            stock_adj_found.updated_at = datetime.datetime.now(datetime.UTC)
            db.add(stock_adj_found)
            db.commit()
            db.refresh(stock_adj_found)
            return stock_adj_found

    @staticmethod
    def group_all_stock_adjustments_for_stocks():
        with DBSession() as db:
            query = db.query(
                StockAdjustment.barcode,
                func.sum(StockAdjustment.quantity).label("total_quantity"),
                StockAdjustment.department_id,
            ).group_by(StockAdjustment.barcode)
            return parse_stock_adjustment_data(query.all())

    @staticmethod
    def get_grouped_stock_adjustments_by_barcode(barcode: str):
        with DBSession() as db:
            query = (
                db.query(
                    StockAdjustment.barcode,
                    func.sum(StockAdjustment.quantity).label("total_quantity"),
                    StockAdjustment.department_id,
                )
                .filter(StockAdjustment.barcode == barcode)
                .group_by(StockAdjustment.barcode)
            )
            return parse_stock_adjustment_data(query.one_or_none())
