from typing import TypeVar

from models.barcode import Barcode
from models.stock_running import StockRunning
from utils.enum import RunningStockStatus
from utils.session import DBSession
from schemas.stock import StockQuery
from utils.countFilter import StockFilter
from typing import Union

StockOperator = TypeVar("StockOperator")


class StockRunningOperator:

    @staticmethod
    def create_running_stock(
        barcode: str,
        stock_operator: StockOperator,
        stock_changes: dict[str, int] = {},
        should_delete_quantity: bool = False,
    ) -> StockRunning:
        """
        Creates or updates the running stock for a given barcode.

        Args:
            barcode: The barcode of the stock.
            stock_operator: An object providing methods to access stock data.
            stock_changes: A dictionary containing optional stock changes:
                - add_stock_quantity (int): Amount of stock to add. Defaults to 0.
                - out_quantity (int): Amount of stock used or removed. Defaults to 0.
                - adjustment_quantity (int): Amount of stock adjusted (positive or negative). Defaults to 0.
            should_delete_quantity: Flag indicating whether to delete the quantity from stock (for order fulfillment). Defaults to False.

        Returns:
            The updated StockRunning object.

        Raises:
            ValueError: If no stocks available for the barcode.
        """

        stock_data = stock_operator.get_grouped_stocks_with_stock_barcode(barcode)
        if not stock_data:
            raise ValueError("No stocks available for barcode")

        quantity = stock_data.get("quantity", 0)
        existing_stock = StockRunningOperator.get_stock_in_inventory(barcode)

        if existing_stock:
            # Update existing stock
            StockRunningOperator.update_stock(existing_stock, stock_changes, quantity, should_delete_quantity)
        else:
            # Create new stock
            remaining_quantity = quantity - (stock_changes.get("adjustment_quantity", 0) + stock_changes.get("out_quantity", 0))
            new_running_stock = StockRunning(
                barcode_id=stock_data.get("id"),
                stock_quantity=quantity,
                **stock_changes,
                remaining_quantity=remaining_quantity,
                status=(
                    RunningStockStatus.re_order.name
                    if remaining_quantity < 10
                    else RunningStockStatus.available.name
                ),
            )
            return new_running_stock.save()

        StockRunningOperator.update_status(existing_stock)
        return existing_stock.save(merge=True)

    @staticmethod
    def update_stock(stock: StockRunning, changes: dict, total_quantity: int, should_delete: bool):
        """
        Updates an existing StockRunning object with the provided changes.

        Args:
            stock: The StockRunning object to update.
            changes: A dictionary containing stock changes (same as in create_running_stock).
            total_quantity: The total stock quantity.
            should_delete: Whether the quantity should be deleted from stock.
        """

        for key, value in changes.items():
            if key == "out_quantity" and value:
                stock.out_quantity = value
                stock.remaining_quantity -= value
            elif key == "adjustment_quantity" and value != -1:
                stock.adjustment_quantity = value
                stock.remaining_quantity -= value
            elif key == "add_stock_quantity":
                stock.stock_quantity += value
                stock.remaining_quantity = total_quantity
            else:
                if not should_delete:
                    stock.remaining_quantity = total_quantity
                else:
                    stock.remaining_quantity -= value
                    stock.stock_quantity -= value

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
    # @staticmethod
    # def create_running_stock(
    #     barcode: str,
    #     stock_operator: StockOperator,
    #     add_stock_quantity: int = 0,
    #     out_quantity: int = 0,
    #     adjustment_quantity: int = 0,
    #     order_quantity: int = 0,
    #     should_delete_quantity: bool = False,
    # ):
    #     stock_data: dict[str, Any] = (
    #         stock_operator.get_grouped_stocks_with_stock_barcode(barcode)
    #     )
    #     if not stock_data:
    #         raise ValueError("No stocks available for barcode")
    #     quantity = stock_data.get("quantity", 0)
    #     running_stock_found = StockRunningOperator.get_stock_in_inventory(barcode)
    #     if not running_stock_found:
    #         remaining_quantity = quantity - (adjustment_quantity + out_quantity)
    #         new_running_stock = StockRunning(
    #             barcode_id=stock_data.get("id"),
    #             stock_quantity=quantity,
    #             out_quantity=out_quantity,
    #             adjustment_quantity=adjustment_quantity,
    #             remaining_quantity=remaining_quantity,
    #             status=(
    #                 RunningStockStatus.re_order.name
    #                 if remaining_quantity < 10
    #                 else RunningStockStatus.available.name
    #             ),
    #         )
    #         return new_running_stock.save()
    #     if out_quantity:
    #         running_stock_found.out_quantity = out_quantity
    #         running_stock_found.remaining_quantity -= order_quantity
    #     elif adjustment_quantity:
    #         if adjustment_quantity == -1:
    #             running_stock_found.adjustment_quantity = 0
    #             running_stock_found.remaining_quantity = quantity
    #         else:
    #             running_stock_found.adjustment_quantity = adjustment_quantity
    #             running_stock_found.remaining_quantity -= order_quantity

    #     elif add_stock_quantity:
    #         running_stock_found.stock_quantity += add_stock_quantity
    #         running_stock_found.remaining_quantity = quantity
    #     else:
    #         if not should_delete_quantity:
    #             running_stock_found.remaining_quantity = quantity
    #         else:
    #             running_stock_found.remaining_quantity -= order_quantity
    #             running_stock_found.stock_quantity -= order_quantity
    #     if running_stock_found.remaining_quantity < 10:
    #         running_stock_found.status = RunningStockStatus.re_order.name
    #     else:
    #         running_stock_found.status = RunningStockStatus.available.name
    #     return running_stock_found.save(merge=True)

    @staticmethod
    def get_stock_in_inventory(barcode_id: Union[int, str]):
        with DBSession() as db:
            if isinstance(barcode_id, int):
                barcode_found = db.query(Barcode).filter(Barcode.id == barcode_id).first()
            else:
                barcode_found = db.query(Barcode).filter(Barcode.barcode == barcode_id).first()
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