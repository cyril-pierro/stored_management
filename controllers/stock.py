import datetime
from typing import Any, Union

from sqlalchemy import and_, func

from controllers.stock_running import StockRunningOperator as SR
from controllers.stock_out import StockOutOperator as SO
from error import AppError
from models.barcode import Barcode
from models.stock import Stock
from models.category import Category
from models.evaluation import CostEvaluation
from schemas.stock import StockIn, BarcodeIn, UpdateIn
from utils.generate import generate_codes
from utils.session import DBSession


def parse_stock_data(stock_data: Union[Any, list, None]):
    if not stock_data:
        return stock_data

    if isinstance(stock_data, list):
        return [
            {
                "id": data[0].id,
                "barcode": data[0].barcode,
                "code": data[0].code,
                "specification": data[0].specification,
                "location": data[0].location,
                "quantity": data[1],
                "prices": data[2],
            }
            for data in stock_data
        ]
    return {
        "id": stock_data[0].id,
        "barcode": stock_data[0].barcode,
        "code": stock_data[0].code,
        "specification": stock_data[0].specification,
        "location": stock_data[0].location,
        "quantity": stock_data[1],
        "prices": stock_data[2],
    }


class StockOperator:
    @staticmethod
    def get_all_stocks():
        with DBSession() as db:
            return db.query(Stock).filter(Stock.cancelled.is_(False)).order_by(Stock.id.desc()).all()

    @staticmethod
    def get_all_barcodes():
        with DBSession() as db:
            return db.query(Barcode).order_by(Barcode.id.desc()).all()

    @staticmethod
    def add_stock(data: StockIn, staff_id: int):
        barcode_found = StockOperator.get_barcode(data.barcode_id)
        cost_allocated = data.__dict__.pop("cost")
        quantity_allocated = data.__dict__.pop("quantity")
        if not barcode_found:
            raise AppError(message="Invalid Barcode Provided", status_code=400)
        new_stock = Stock(
            barcode_id=barcode_found.id,
            created_by=staff_id,
            cost=cost_allocated,
            quantity=quantity_allocated,
            quantity_initiated=quantity_allocated,
        )
        value = new_stock.save()
        SR.create_running_stock(
            barcode=barcode_found.barcode,
            stock_operator=StockOperator,
            add_stock_quantity=quantity_allocated,
        )
        return value

    @staticmethod
    def update_stock_and_cost(
        quantity: int,
        barcode_id: int,
        order_id: int,
    ) -> Union[float, None]:
        total_cost = 0
        with DBSession() as db:
            stocks = (
                db.query(Stock)
                .filter(and_(Stock.barcode_id == barcode_id, Stock.sold.is_(False)))
                .order_by(Stock.id.asc())
                .all()
            )
            if len(stocks) == 0:
                return
            for stock in stocks:
                should_break = False
                if stock.quantity >= quantity:
                    stock.quantity -= quantity
                    StockOperator.add_cost_evaluation_data(
                        stock_obj=stock, quantity=quantity
                    )
                    if stock.quantity == 0:
                        stock.sold = True
                    stock.sold_at = datetime.datetime.now()
                    db.add(stock)
                    db.commit()
                    db.refresh(stock)
                    SO.create_stock_out(
                        barcode_id=barcode_id,
                        quantity=quantity,
                        order_id=order_id,
                        cost=stock.cost
                    )
                    total_cost += stock.cost * quantity
                    should_break = True

                else:
                    old_quantity = stock.quantity
                    quantity = quantity - stock.quantity
                    stock.quantity = 0
                    stock.sold = True
                    stock.sold_at = datetime.datetime.now()
                    db.add(stock)
                    db.commit()
                    db.refresh(stock)
                    StockOperator.add_cost_evaluation_data(
                        stock_obj=stock,
                        quantity=old_quantity,
                    )
                    SO.create_stock_out(
                        barcode_id=barcode_id,
                        quantity=old_quantity,
                        order_id=order_id,
                        cost=stock.cost
                    )
                    total_cost += stock.cost * old_quantity
                if should_break:
                    break
        return total_cost

    @staticmethod
    def get_all_stocks_not_sold(barcode_id: int) -> list[Stock]:
        with DBSession() as db:
            return db.query(Stock)\
                .filter(and_(Stock.barcode_id == barcode_id, Stock.sold.is_(False), Stock.cancelled.is_(False)))\
                .order_by(Stock.id.asc())\
                .all()

    @staticmethod
    def add_cost_evaluation_data(stock_obj: Stock, quantity: int):
        new_cost_data = CostEvaluation(
            barcode_id=stock_obj.barcode_id,
            cost=stock_obj.cost,
            quantity=quantity,
            total=round(float(quantity * stock_obj.cost), 2),
        )
        new_cost_data.save()

    @staticmethod
    def get_all_cost_evaluation_data():
        with DBSession() as db:
            return db.query(CostEvaluation).order_by(CostEvaluation.id.desc()).all()

    @staticmethod
    def group_all_stock_barcode():
        with DBSession() as db:
            query = (
                db.query(
                    Barcode,
                    func.sum(Stock.quantity_initiated).label("total_quantity"),
                    func.array_agg(Stock.cost).label("cost_list"),
                )
                .join(Stock, Barcode.id == Stock.barcode_id)
                .filter(Stock.cancelled.is_(False))
                .group_by(Barcode)
            )
        return parse_stock_data(query.all())

    @staticmethod
    def get_grouped_stocks_with_stock_barcode(barcode: str):
        """
        Retrieve grouped stock information associated with a specific barcode.
        This function aggregates stock quantities and costs
        for the given barcode, providing a summary of stock data.

        Args:
            barcode (str): The barcode for which the grouped
            stock information is requested.

        Returns:
            dict or None: A dictionary containing the total quantity of stock
            and a list of associated costs, or None if no data is found.
        """
        with DBSession() as db:
            query = (
                db.query(
                    Barcode,
                    func.sum(Stock.quantity).label("total_quantity"),
                    func.sum(Stock.cost * Stock.quantity_initiated),
                )
                .join(Stock, Barcode.id == Stock.barcode_id)
                .filter(and_(Barcode.barcode == barcode, Stock.cancelled.is_(False)))
                .group_by(Barcode)
            )
        return parse_stock_data(query.one_or_none())

    @staticmethod
    def get_stock_report(
        barcode: str,
        from_datetime: Any,
        to_datetime: Any
    ):
        """
        Retrieve a stock report for a specific barcode within a given time
        frame. This function queries the stock data associated with
        the provided barcode and groups the results by month,
        allowing for analysis of stock trends over time.

        Args:
            barcode (str): The barcode for which the stock report is generated.
            report_on (Any, optional): The date up to which the report
            is generated. Defaults to the current date and time.

        Returns:
            list: A list of stock report data grouped by month for the 
            specified barcode.
        """
        if not from_datetime:
            condition = Stock.created_at <= to_datetime
        else:
            condition = Stock.created_at.between(
                from_datetime, to_datetime
            )

        with DBSession() as db:
            return db.query(Stock)\
                .filter(
                    and_(
                        Stock.barcode.has(Barcode.barcode == barcode),
                        Stock.cancelled.is_(False),
                        condition
                    )
            ).order_by(Stock.id.asc()).all()

    @staticmethod
    def get_stock_by(id_or_barcode: Union[str, int]):
        with DBSession() as db:
            return db.query(Stock).filter(and_(Stock.id == id_or_barcode, Stock.cancelled.is_(False))).first()

    @staticmethod
    def get_barcode(barcode: Union[str, int]):
        with DBSession() as db:
            if isinstance(barcode, str):
                return db.query(Barcode).filter(Barcode.barcode == barcode).first()
            return db.query(Barcode).filter(Barcode.id == barcode).first()

    @staticmethod
    def update_stock(stock_id: int, data: StockIn, staff_id: int):
        values = data.__dict__
        quantity = values.pop("quantity")
        stock_found = StockOperator.get_stock_by(stock_id)
        if not stock_found:
            raise ValueError("Stock not found")
        if stock_found.sold_at or stock_found.sold:
            raise AppError(
                message="Sorry, can't update this stock info, it is in use",
                status_code=400,
            )
        # update stock details
        stock_found.updated_at = datetime.datetime.now()
        stock_found.barcode_id = data.barcode_id
        stock_found.updated_by = staff_id
        stock_found.quantity = quantity
        stock_found.quantity_initiated = quantity
        stock_found.updated_at = datetime.datetime.now()
        stock_found.cost = data.cost
        SR.create_running_stock(
            barcode=stock_found.barcode.barcode,
            stock_operator=StockOperator,
        )
        stock_found.save(merge=True)
        return stock_found

    @staticmethod
    def remove_stock(stock_id: int):
        with DBSession() as db:
            stock_found = db.query(Stock).filter(Stock.id == stock_id).first()
            if not stock_found:
                raise ValueError("Stock not found")
            if stock_found.sold_at or stock_found.sold:
                raise AppError(
                    message="Sorry, can't delete this stock, it is in use",
                    status_code=400,
                )
            quantity = stock_found.quantity
            barcode_value = stock_found.barcode.barcode
            SR.create_running_stock(
                barcode=barcode_value,
                stock_operator=StockOperator,
                should_delete_quantity=True,
                order_quantity=quantity,
            )
            db.delete(stock_found)
            db.commit()
        return True

    @staticmethod
    def mark_stock_as_cancelled(stock_id: int) -> bool:
        stock_found = StockOperator.get_stock_by(stock_id)
        if not stock_found:
            raise AppError(message="Stock not found", status_code=404)
        stock_found.update({"cancelled": True})
        barcode_value = stock_found.barcode.barcode
        SR.handle_cancelled_stocks(
            barcode=barcode_value,
            quantity=stock_found.quantity_initiated,
        )
        return True


class ScanStock:
    @staticmethod
    def add_barcode(data: BarcodeIn) -> Barcode:
        with DBSession() as db:
            found_barcode = (
                db.query(Barcode).filter(
                    Barcode.barcode == data.barcode).first()
            )
            if found_barcode:
                raise AppError(
                    message="Scan Barcode already exists", status_code=400)
            # get the last barcode added
            last_barcode = (
                db.query(Barcode)
                .filter(Barcode.code.ilike(f"%SK{data.category.upper()[0]}%"))
                .order_by(Barcode.id.desc())
                .first()
            )
        category_found = Category.get(data.category)
        if not category_found:
            raise ValueError(
                "Please enter a category before you add a barcode")

        data.__dict__["code"] = generate_codes(
            previous_code=last_barcode.code if last_barcode else None,
            category=data.category,
        )
        data.__dict__["category_id"] = category_found.id
        data.__dict__.pop("category")
        scan_created = Barcode(**data.__dict__)
        return scan_created.save()

    @staticmethod
    def get_barcode(barcode_id: int) -> Barcode:
        with DBSession() as db:
            found_barcode = db.query(Barcode).filter(
                Barcode.id == barcode_id).first()
            if not found_barcode:
                raise AppError(
                    message="Scan Barcode does not exist", status_code=404)
        return found_barcode

    @staticmethod
    def edit_barcode(barcode_id: int, data: UpdateIn) -> Barcode:
        barcode_found = ScanStock.get_barcode(barcode_id)
        barcode_found.barcode = data.barcode
        barcode_found.location = data.location
        barcode_found.specification = data.specification
        barcode_found.erm_code = data.erm_code or barcode_found.erm_code
        return barcode_found.save(merge=True)

    @staticmethod
    def delete_barcode(barcode_id: int) -> bool:
        with DBSession() as db:
            found_barcode = db.query(Barcode).filter(
                Barcode.id == barcode_id).first()
            if not found_barcode:
                raise AppError(
                    message="Scan Barcode does not exist", status_code=404)
            stock_available = (
                db.query(Stock).filter(
                    Stock.barcode_id == found_barcode.id).first()
            )
            if stock_available:
                raise AppError(
                    message="Action denied, Scan Barcode is in use as a Stock",
                    status_code=400,
                )
            db.delete(found_barcode)
            db.commit()
        return True
