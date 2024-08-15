import datetime
from typing import Any, Union

from sqlalchemy import and_, func

from controllers.stock_running import StockRunningOperator as SR
from models.barcode import Barcode
from models.cost import Costs
from models.stock import Stock
from schemas.stock import StockIn
from utils.generate import generate_codes
from utils.session import DBSession
from error import AppError


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
                "prices": set(data[2].split(",")),
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
        "prices": set(stock_data[2].split(",")),
    }


class StockOperator:
    @staticmethod
    def get_all_stocks():
        with DBSession() as db:
            return db.query(Stock).all()

    @staticmethod
    def get_all_barcodes():
        with DBSession() as db:
            return db.query(Barcode).all()

    @staticmethod
    def get_or_generate_cost(
        cost: float,
    ) -> Costs:
        with DBSession() as db:
            cost_found = (
                db.query(Costs)
                .filter(
                    and_(
                        Costs.cost == cost,
                    )
                )
                .first()
            )
            if not cost_found:
                new_cost = Costs(
                    cost=cost,
                )
                db.add(new_cost)
                db.commit()
                db.refresh(new_cost)
                return new_cost
            return cost_found

    @staticmethod
    def add_stock(data: StockIn, staff_id: int):
        barcode_found = StockOperator.get_barcode(data.barcode)
        cost_allocated = data.__dict__.pop("cost")
        quantity_allocated = data.__dict__.pop("quantity")
        if not barcode_found:
            last_stock_added = Barcode.get_last_stock()
            code = last_stock_added.code if last_stock_added else None
            new_code = generate_codes(code)
            data.__dict__["code"] = new_code
            new_barcode = Barcode(**data.__dict__)
            barcode_found = new_barcode.save()
        cost_created = StockOperator.get_or_generate_cost(cost=cost_allocated)
        new_stock = Stock(
            barcode_id=barcode_found.id,
            created_by=staff_id,
            cost_id=cost_created.id,
            quantity=quantity_allocated,
        )
        value = new_stock.save()
        SR.create_running_stock(
            barcode=data.barcode,
            stock_operator=StockOperator,
            add_stock_quantity=quantity_allocated
        )
        return value

    @staticmethod
    def update_stock_and_cost(quantity: int, barcode_id: int) -> Union[bool, None]:
        with DBSession() as db:
            stocks = (
                db.query(Stock)
                .filter(and_(Stock.barcode_id == barcode_id, Stock.sold == False))
                .all()
            )
            if len(stocks) == 0:
                return
            for stock in stocks:
                if stock.quantity >= quantity:
                    stock.quantity -= quantity
                    if stock.quantity == 0:
                        stock.sold = True
                    stock.updated_at = datetime.datetime.now(datetime.UTC)
                    db.commit()
                    db.refresh(stock)
                else:
                    quantity = quantity - stock.quantity
                    stock.quantity = 0
                    stock.sold = True
                    stock.updated_at = datetime.datetime.now(datetime.UTC)
                    db.commit()
                    db.refresh(stock)
            return True

    @staticmethod
    def group_all_stock_barcode():
        with DBSession() as db:
            query = (
                db.query(
                    Barcode,
                    func.sum(Stock.quantity).label("total_quantity"),
                    func.group_concat(Costs.cost).label("cost_list"),
                )
                .join(Stock, Barcode.id == Stock.barcode_id)
                .join(Costs, Stock.cost_id == Costs.id)
                .group_by(Barcode)
            )
        return parse_stock_data(query.all())

    @staticmethod
    def get_grouped_stocks_with_stock_barcode(barcode: str):
        with DBSession() as db:
            query = (
                db.query(
                    Barcode,
                    func.sum(Stock.quantity).label("total_quantity"),
                    func.group_concat(Costs.cost).label("cost_list"),
                )
                .join(Stock, Barcode.id == Stock.barcode_id)
                .join(Costs, Stock.cost_id == Costs.id)
                .filter(Barcode.barcode == barcode)
                .group_by(Barcode)
            )
        return parse_stock_data(query.one_or_none())

    @staticmethod
    def get_stock_by(id_or_barcode: Union[str, int]):
        with DBSession() as db:
            return db.query(Stock).filter(Stock.id == id_or_barcode).first()

    @staticmethod
    def get_barcode(barcode: Union[str, int]):
        with DBSession() as db:
            if isinstance(barcode, str):
                return db.query(Barcode).filter(Barcode.barcode == barcode).first()
            return db.query(Barcode).filter(Barcode.id == barcode).first()

    @staticmethod
    def update_stock(stock_id: int, data: StockIn, staff_id: int):
        values = data.__dict__
        values["updated_by"] = staff_id
        values["updated_at"] = datetime.datetime.now(datetime.UTC)
        stock_found = StockOperator.get_stock_by(stock_id)
        if not stock_found:
            raise ValueError("Stock not found")
        if stock_found.updated_at or stock_found.sold:
            raise AppError(
                message="Sorry, can't update this stock info, it is in use",
                status_code=400
            )
        # update stock details
        with DBSession() as db:
            query = db.query(Barcode).filter(Barcode.id == stock_found.barcode_id)
            query.update(values, synchronize_session=False)
            db.commit()
            updated_instance = query.one_or_none()
            SR.create_running_stock(
                barcode=data.barcode,
                stock_operator=StockOperator,
            )
            stock_found.save()
            return updated_instance

    @staticmethod
    def remove_stock(stock_id: int):
        with DBSession() as db:
            stock_found = db.query(Stock).filter(Stock.id == stock_id).first()
            if not stock_found:
                raise ValueError("Stock not found")
            if stock_found.updated_at or stock_found.sold:
                raise AppError(
                    message="Sorry, can't delete this stock, it is in use",
                    status_code=400
                )
            quantity = stock_found.quantity
            db.delete(stock_found)
            db.commit()
            SR.create_running_stock(
                barcode=stock_found.barcode,
                stock_operator=StockOperator,
                should_delete_quantity=True,
                order_quantity=quantity
            )
            return True
