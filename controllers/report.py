from models.staff import Staff
from models.department import Department
from models.stock_adjustment import StockAdjustment
from models.order import Orders
from models.barcode import Barcode
from utils.session import DBSession
from sqlalchemy import func
from parser.report import ReportParser


class ReportDashboard:
    @staticmethod
    def get_number_of_engineers_in_each_department():
        with DBSession() as db:
            return ReportParser.convert_engineers_to_departments_data(
                db.query(Department, func.count(Staff.id))
                .join(Staff, Staff.department_id == Department.id)
                .group_by(Staff.department_id)
                .all()
            )

    @staticmethod
    def get_department_adjustment_order():
        with DBSession() as db:
            subq_adjustments = (
                db.query(
                    StockAdjustment.department_id,
                    func.sum(StockAdjustment.quantity).label("adjustment_amount"),
                )
                .group_by(StockAdjustment.department_id)
                .subquery()
            )

            subq_orders = (
                db.query(
                    Staff.department_id, func.sum(Orders.quantity).label("sale_amount")
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
            return ReportParser.convert_number_and_quantity_orders_data(
                data=db.query(
                    Department.name, func.count(Orders.id), func.sum(Orders.quantity)
                )
                .outerjoin(
                    Orders, Orders.staff.has(Staff.department_id == Department.id)
                )
                .group_by(Department.name)
                .all()
            )

    @staticmethod
    def get_erm_report_data():
        with DBSession() as db:
            value = (
                db.query(Orders)
                .filter(Orders.barcode.has(Barcode.erm_code.is_not(None)))
                .all()
            )
            return [i.erm_report() for i in value]
