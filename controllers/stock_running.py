from typing import Any, TypeVar

from models.barcode import Barcode
from models.stock_running import StockRunning
from utils.enum import RunningStockStatus
from utils.session import DBSession
from schemas.stock import StockQuery
from utils.countFilter import StockFilter

StockOperator = TypeVar("StockOperator")


class StockRunningOperator:
    @staticmethod
    def create_running_stock(
        barcode: str,
        stock_operator: StockOperator,
        add_stock_quantity: int = 0,
        out_quantity: int = 0,
        adjustment_quantity: int = 0,
        order_quantity: int = 0,
        should_delete_quantity: bool = False,
    ):
        stock_data: dict[str, Any] = (
            stock_operator.get_grouped_stocks_with_stock_barcode(barcode)
        )
        if not stock_data:
            raise ValueError("No stocks available for barcode")
        quantity = stock_data.get("quantity", 0)
        running_stock_found = StockRunningOperator.get_stock_in_inventory(barcode)
        if not running_stock_found:
            remaining_quantity = quantity - (adjustment_quantity + out_quantity)
            new_running_stock = StockRunning(
                barcode_id=stock_data.get("id"),
                stock_quantity=quantity,
                out_quantity=out_quantity,
                adjustment_quantity=adjustment_quantity,
                remaining_quantity=remaining_quantity,
                status=(
                    RunningStockStatus.re_order.name
                    if remaining_quantity < 10
                    else RunningStockStatus.available.name
                ),
            )
            return new_running_stock.save()
        if out_quantity:
            running_stock_found.out_quantity = out_quantity
            running_stock_found.remaining_quantity -= order_quantity
        elif adjustment_quantity:
            if adjustment_quantity == -1:
                running_stock_found.adjustment_quantity = 0
                running_stock_found.remaining_quantity = quantity
            else:
                running_stock_found.adjustment_quantity = adjustment_quantity
                running_stock_found.remaining_quantity -= order_quantity

        elif add_stock_quantity:
            running_stock_found.stock_quantity += add_stock_quantity
            running_stock_found.remaining_quantity = quantity
        else:
            running_stock_found.remaining_quantity = (
                quantity
                if not should_delete_quantity
                else running_stock_found.remaining_quantity - order_quantity
            )
        if running_stock_found.remaining_quantity < 10:
            running_stock_found.status = RunningStockStatus.re_order.name
        else:
            running_stock_found.status = RunningStockStatus.available.name
        return running_stock_found.save(merge=True)

    @staticmethod
    def get_stock_in_inventory(barcode: str):
        with DBSession() as db:
            barcode_found = db.query(Barcode).filter(Barcode.barcode == barcode).first()
            if not barcode_found:
                raise ValueError("Could not find barcode in inventory")
            return (
                db.query(StockRunning)
                .filter(StockRunning.barcode_id == barcode_found.id)
                .first()
            )

    @staticmethod
    def get_all_running_stocks(query_params: StockQuery = None):
        stock_filter = StockFilter(query_params, db_model=StockRunning)
        return stock_filter.apply()