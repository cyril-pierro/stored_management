from controllers.stock import StockOperator
from controllers.stock_running import StockRunningOperator
from controllers.stock_out import StockOutOperator as SO
from models.order import Orders
from schemas.order import OrderIn
from utils.enum import OrderStatus
from utils.enum import RunningStockStatus as RS
from utils.session import DBSession


class OrderOperator:
    @staticmethod
    def check_if_order_is_available(barcode: str):
        stock = StockOperator.get_stock_by(barcode)
        if not stock:
            raise ValueError("No stock available with barcode specified")
        running_stock = StockRunningOperator.get_stock_in_inventory(barcode)
        return {
            "barcode": barcode,
            "specification": stock.specification,
            "location": stock.location,
            "available": running_stock.status,
        }

    @staticmethod
    def get_all_orders():
        with DBSession() as db:
            return db.query(Orders).all()

    @staticmethod
    def get_number_of_orders():
        return len(OrderOperator.get_all_orders())

    @staticmethod
    def create_order_for_stock_with(barcode: str, data: OrderIn, user_id: int = 1):
        running_stock = StockRunningOperator.get_stock_in_inventory(barcode)
        if not running_stock:
            raise ValueError("Barcode for stock not found")

        new_order = Orders(
            barcode=barcode,
            staff_id=user_id,
            job_number=data.job_number,
            quantity=data.quantity,
            restrictions=OrderStatus.part_available.name
            if data.status.name == RS.available.name
            else OrderStatus.part_not_available.name,
        )
        created_order = new_order.save()
        
