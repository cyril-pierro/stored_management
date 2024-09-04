from models.staff import Staff
from models.department import Department
from models.stock_adjustment import StockAdjustment
from models.order import Orders
from models.barcode import Barcode
from controllers.stock_running import StockRunningOperator
from utils.session import DBSession
from sqlalchemy import func, select, desc
from parser.report import ReportParser
from typing import Any


class ReportDashboard:
    @staticmethod
    def get_number_of_engineers_in_each_department():
        with DBSession() as db:
            data = db.query(Department, func.count(Staff.id)) \
                .join(Staff, Staff.department_id == Department.id) \
                .group_by(Staff.department_id, Department.id) \
                .all()
        return ReportParser.convert_engineers_to_departments_data(data)

    @staticmethod
    def get_department_adjustment_order():
        with DBSession() as db:
            subq_adjustments = (
                db.query(
                    StockAdjustment.department_id,
                    func.sum(StockAdjustment.quantity).label(
                        "adjustment_amount"),
                )
                .group_by(StockAdjustment.department_id)
                .subquery()
            )

            subq_orders = (
                db.query(
                    Staff.department_id, func.sum(
                        Orders.quantity).label("sale_amount")
                )
                .join(Orders, Staff.id == Orders.staff_id)
                .group_by(Staff.department_id)
                .subquery()
            )

            query = (
                db.query(
                    Department.name,
                    subq_adjustments.c.adjustment_amount,
                    subq_orders.c.sale_amount,
                )
                .outerjoin(
                    subq_adjustments, Department.id == subq_adjustments.c.department_id
                )
                .outerjoin(subq_orders, Department.id == subq_orders.c.department_id)
            )

        return ReportParser.convert_department_adjustment_orders_data(
            data=query.all()
        )

    @staticmethod
    def get_number_and_quantity_orders_each_department():
        with DBSession() as db:
            data = db.query(
                Department.name, func.count(
                    Orders.id), func.sum(Orders.quantity)
            )\
                .outerjoin(
                    Orders, Orders.staff.has(
                        Staff.department_id == Department.id)
            )\
                .group_by(Department.name)\
                .all()
        return ReportParser.convert_number_and_quantity_orders_data(data)

    @staticmethod
    def get_erm_report_data():
        with DBSession() as db:
            orders = db.query(Orders).filter(Orders.barcode.has(
                Barcode.erm_code.is_not(None))).order_by(Orders.id.desc()).all()
        if len(orders) == 0:
            return []
        return [
            {
                "id": order.id,
                "date": order.created_at.isoformat(),
                "event_number": order.job_number,
                "part_code": order.barcode.barcode,
                "part_type": order.part_name,
                "part_description": order.barcode.specification,
                "quantity": order.quantity,
                "erm_code": order.barcode.erm_code,
            }
            for order in orders
        ]

    # @staticmethod
    # def get_analysis_for_barcode(barcode: str) -> dict[str, Any]:
    #     running_stock = StockRunningOperator.get_stock_in_inventory(barcode)
