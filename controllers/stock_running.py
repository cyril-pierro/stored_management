from typing import TypeVar, Any

from models.barcode import Barcode
from models.stock_running import StockRunning
from utils.enum import RunningStockStatus
from utils.session import DBSession
from schemas.stock import StockQuery
from utils.countFilter import StockFilter
from controllers.stock_out import StockOutOperator
from typing import Union
from datetime import datetime as dt
from sqlalchemy import and_

StockOperator = TypeVar("StockOperator")
StockAdjustmentOperator = TypeVar("StockAdjustmentOperator")


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
        stock_adjustment_op: StockAdjustmentOperator = None,
    ) -> StockRunning:
        stock_data = stock_operator.get_grouped_stocks_with_stock_barcode(
            barcode)
        total_stock_adjustment_value = 0
        if not stock_data:
            raise ValueError("No stocks available for barcode")

        quantity = stock_data.get("quantity", 0)
        total_stock_value = stock_data.get("prices", 0)
        total_stock_out_value = StockOutOperator.get_all_stock_outs_for_barcode(
            barcode)
        if stock_adjustment_op:
            total_stock_adjustment_value = stock_adjustment_op.get_stock_adjustments_value(
                barcode=barcode
            )
        existing_stock = StockRunningOperator.get_stock_in_inventory(barcode)
        total_cost = total_stock_value - \
            ((total_stock_out_value or 0) + (total_stock_adjustment_value or 0))
        if existing_stock:
            # Update existing stock
            updated_stock = StockRunningOperator.update_stock(
                running_stock_found=existing_stock,
                quantity=quantity,
                out_quantity=out_quantity,
                adjustment_quantity=adjustment_quantity,
                add_stock_quantity=add_stock_quantity,
                order_quantity=order_quantity,
                should_delete_quantity=should_delete_quantity,
            )
            updated_status = StockRunningOperator.update_status(updated_stock)
            updated_status.cost = total_cost
            return updated_status.save(merge=True)
        else:
            # Create new stock
            remaining_quantity = quantity - \
                (adjustment_quantity + out_quantity)
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
            new_running_stock.cost = total_cost
            return new_running_stock.save()
        
    @staticmethod
    def handle_cancelled_stocks(barcode: str, quantity: int):
        existing_stock = StockRunningOperator.get_stock_in_inventory(barcode)
        if existing_stock:
            StockRunningOperator.update_stock(
                existing_stock,
                order_quantity=quantity,
                should_delete_quantity=True
            ).save(merge=True)

    @staticmethod
    def update_stock(
        running_stock_found: StockRunning,
        quantity: int = 0,
        add_stock_quantity: int = 0,
        out_quantity: int = 0,
        adjustment_quantity: int = 0,
        order_quantity: int = 0,
        should_delete_quantity: bool = False,
    ) -> StockRunning:
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
            if not should_delete_quantity:
                running_stock_found.remaining_quantity = quantity
            else:
                running_stock_found.remaining_quantity -= order_quantity
                running_stock_found.stock_quantity -= order_quantity
        return running_stock_found

    @staticmethod
    def update_status(stock: StockRunning):
        """
        Updates the status of the StockRunning object based on remaining quantity.
        """

        stock.status = (
            RunningStockStatus.re_order.name
            if stock.remaining_quantity < 10
            else RunningStockStatus.available.name
        )
        return stock

    @staticmethod
    def get_stock_in_inventory(barcode_id: Union[int, str]) -> StockRunning:
        with DBSession() as db:
            if isinstance(barcode_id, int):
                barcode_found = db.query(Barcode).filter(
                    Barcode.id == barcode_id).first()
            else:
                barcode_found = db.query(Barcode).filter(
                    Barcode.barcode == barcode_id).first()
            if not barcode_found:
                raise ValueError("Could not find barcode in inventory")
            return (
                db.query(StockRunning)
                .filter(StockRunning.barcode_id == barcode_found.id)
                .first()
            )

    @staticmethod
    def get_running_stock_report(
        barcode_id: Union[int, str],
        report_on: Any = dt.now()
    ) -> StockRunning:
        with DBSession() as db:
            return db.query(StockRunning)\
                .filter(
                    and_(
                        StockRunning.barcode.has(
                            Barcode.barcode == barcode_id),
                        StockRunning.updated_at <= report_on,
                    )
            ).first()

    @staticmethod
    def get_all_running_stocks(query_params: StockQuery = None):
        stock_filter = StockFilter(query_params, db_model=StockRunning)
        return stock_filter.apply()
