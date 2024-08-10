from typing import Any, TypeVar

from models.stock_running import StockRunning
from utils.enum import RunningStockStatus
from utils.session import DBSession

StockOperator = TypeVar("StockOperator")


class StockRunningOperator:
    @staticmethod
    def create_running_stock(
        barcode: str,
        stock_operator: StockOperator,
        out_quantity: int = 0,
        adjustment_quantity: int = 0,
        should_delete_quantity: bool = False,
    ):
        stock_data: dict[
            str, Any
        ] = stock_operator.get_grouped_stocks_with_stock_barcode(barcode)
        quantity = stock_data.get("quantity")
        running_stock_found = StockRunningOperator.get_stock_in_inventory(barcode)
        if not running_stock_found:
            remaining_quantity = quantity - (adjustment_quantity + out_quantity)
            new_running_stock = StockRunning(
                barcode=barcode,
                stock_quantity=quantity,
                out_quantity=out_quantity,
                adjustment_quantity=adjustment_quantity,
                remaining_quantity=remaining_quantity,
                status=RunningStockStatus.re_order.name
                if remaining_quantity < 10
                else RunningStockStatus.available.name,
            )
            return new_running_stock.save()
        if out_quantity:
            running_stock_found.out_quantity = out_quantity
            running_stock_found.remaining_quantity = (
                quantity - running_stock_found.out_quantity
            )
        elif adjustment_quantity:
            running_stock_found.adjustment_quantity = adjustment_quantity
            running_stock_found.remaining_quantity = (
                quantity - running_stock_found.out_quantity
            )
        else:
            running_stock_found.remaining_quantity = (
                quantity
                if not should_delete_quantity
                else running_stock_found.remaining_quantity - quantity
            )
        if (
            quantity
            - (
                running_stock_found.out_quantity
                + running_stock_found.adjustment_quantity
            )
            < 10
        ):
            running_stock_found.status = RunningStockStatus.re_order.name
        running_stock_found.stock_quantity = quantity
        return running_stock_found.save(merge=True)

    @staticmethod
    def get_stock_in_inventory(barcode: str):
        with DBSession() as db:
            return (
                db.query(StockRunning).filter(StockRunning.barcode == barcode).first()
            )

    @staticmethod
    def get_all_running_stocks():
        with DBSession() as db:
            return db.query(StockRunning).all()
