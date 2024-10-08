from controllers.stock import StockOperator
from controllers.stock_out import StockOutOperator as SO
from controllers.stock_running import StockRunningOperator as SR
from models.email import Recipients
from models.order import Orders
from models.barcode import Barcode
from schemas.order import OrderIn
from utils.enum import OrderStatus
from utils.enum import RunningStockStatus as RS
from utils.session import DBSession
from cron.task import send_email
from datetime import datetime, timedelta
from sqlalchemy import and_


class OrderOperator:
    @staticmethod
    def check_if_order_is_available(barcode_id: int):
        stock = StockOperator.get_barcode(barcode_id)
        if not stock:
            raise ValueError("No stock available with barcode specified")
        running_stock = SR.get_stock_in_inventory(barcode_id)
        if not running_stock:
            raise ValueError("No stock available with barcode specified")
        return {
            "barcode": running_stock.barcode.barcode,
            "specification": stock.specification,
            "location": stock.location,
            "available": running_stock.status.name,
            "running_stock": running_stock.remaining_quantity,
        }

    @staticmethod
    def get_all_orders(from_: str = None, to_: str = None):
        filters = []
        if from_:
            from_datetime = datetime.strptime(from_, '%Y-%m-%d')
            filters.append(Orders.created_at >= from_datetime +
                           timedelta(hours=0, minutes=0, seconds=0))
        if to_:
            to_datetime = datetime.strptime(to_, '%Y-%m-%d')
            filters.append(Orders.created_at <= to_datetime +
                           timedelta(hours=23, minutes=59, seconds=59))

        with DBSession() as db:
            if not filters:
                return db.query(Orders).order_by(Orders.id.desc()).all()
            return db.query(Orders).filter(and_(*filters)).order_by(Orders.id.desc()).all()

    @staticmethod
    def get_number_of_orders():
        return len(OrderOperator.get_all_orders())

    @staticmethod
    def create_order_for_stock_with(
        barcode: str, data: OrderIn, user_id: int
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
            part_name=data.part_name,
            quantity=data.quantity,
            available_quantity=running_stock.remaining_quantity,
            restrictions=OrderStatus.part_available.name,
        )
        created_order = new_order.save()

        total_cost = StockOperator.update_stock_and_cost(
            quantity=data.quantity,
            barcode_id=running_stock.barcode_id,
            order_id=created_order.id
        )

        value = SO.get_group_all_stock_ids_data_by_stock_id(barcode)

        stock_runner = SR.create_running_stock(
            barcode,
            stock_operator=StockOperator,
            out_quantity=value.get("quantity", 0),
            order_quantity=data.quantity,
        )
        if stock_runner.status.value == RS.re_order.value:
            # send email to recipients
            OrderOperator.notify_stock_controllers(
                recipients=Recipients.get_all_recipients(),
                barcode=stock_runner.barcode,
            )
        created_order.total_cost = total_cost
        created_order.save(merge=True)
        return created_order

    @staticmethod
    def notify_stock_controllers(recipients: list[Recipients], barcode: Barcode):
        emails = [recipient.email for recipient in recipients]
        send_email.delay(
            email=emails,
            subject="Stock Re-Order Notification Alert",
            content={
                "barcode": barcode.barcode,
                "location": barcode.location,
                "specification": barcode.specification,
            },
        )
