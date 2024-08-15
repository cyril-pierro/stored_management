from fastapi import BackgroundTasks

from controllers.stock import StockOperator
from controllers.stock_out import StockOutOperator as SO
from controllers.stock_running import StockRunningOperator as SR
from models.email import Recipients
from models.order import Orders
from schemas.order import OrderIn
from utils.email import EmailService
from utils.enum import OrderStatus
from utils.enum import RunningStockStatus as RS
from utils.session import DBSession


class OrderOperator:
    @staticmethod
    def check_if_order_is_available(barcode: str):
        stock = StockOperator.get_barcode(barcode)
        if not stock:
            raise ValueError("No stock available with barcode specified")
        running_stock = SR.get_stock_in_inventory(barcode)
        if not running_stock:
            raise ValueError("No stock available with barcode specified")
        # running_stock_value = running_stock.stock_quantity - (running_stock.out_quantity + running_stock.adjustment_quantity)
        return {
            "barcode": barcode,
            "specification": stock.specification,
            "location": stock.location,
            "available": running_stock.status.name,
            "running_stock": running_stock.remaining_quantity,
        }

    @staticmethod
    def get_all_orders():
        with DBSession() as db:
            return db.query(Orders).all()

    @staticmethod
    def get_number_of_orders():
        return len(OrderOperator.get_all_orders())

    @staticmethod
    def create_order_for_stock_with(
        barcode: str, data: OrderIn, user_id: int, background_task: BackgroundTasks
    ):
        running_stock = SR.get_stock_in_inventory(barcode)
        if not running_stock:
            raise ValueError("Sorry, item not found")

        if data.quantity > running_stock.remaining_quantity:
            raise ValueError("Sorry, we are currently out of stock")

        # create order
        new_order = Orders(
            barcode_id=running_stock.barcode_id,
            staff_id=user_id,
            job_number=data.job_number,
            quantity=data.quantity,
            available_quantity=running_stock.remaining_quantity,
            restrictions=OrderStatus.part_available.name,
        )
        created_order = new_order.save()

        # save stock out data
        SO.create_stock_out(
            barcode_id=running_stock.barcode_id,
            quantity=data.quantity,
            order_id=created_order.id,
        )

        value = SO.get_group_all_stock_ids_data_by_stock_id(barcode)

        stock_runner = SR.create_running_stock(
            barcode,
            stock_operator=StockOperator,
            out_quantity=value.get("quantity", 0),
            order_quantity=data.quantity
        )
        if stock_runner.status.value == RS.re_order.value:
            # send email to recipients
            background_task.add_task(
                OrderOperator.notify_stock_controllers,
                recipients=Recipients.get_all_recipients(),
                barcode=stock_runner.barcode.barcode,
            )
        StockOperator.update_stock_and_cost(
            quantity=data.quantity, barcode_id=running_stock.barcode_id
        )
        return created_order

    @staticmethod
    async def notify_stock_controllers(recipients: list[Recipients], barcode: str):
        emails = [recipient.email for recipient in recipients]
        await EmailService.send(
            email=emails,
            subject="Stock Re-Order Notification Alert",
            content={"barcode": barcode},
        )
