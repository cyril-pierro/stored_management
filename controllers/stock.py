import datetime
from typing import Any, Union

from sqlalchemy import func

from controllers.stock_running import StockRunningOperator as SR
from models.stock import Stock
from models.barcode import Barcode
from schemas.stock import StockIn
from utils.generate import generate_codes
from utils.session import DBSession


def parse_stock_data(stock_data: Union[Any, list, None]):
    if not stock_data:
        return stock_data

    if isinstance(stock_data, list):
        return [
            {
                "barcode": data[0],
                "code": data[1],
                "specification": data[2],
                "location": data[3],
                "quantity": data[4],
                "cost": data[5],
            }
            for data in stock_data
        ]
    return {
        "barcode": stock_data[0],
        "code": stock_data[1],
        "specification": stock_data[2],
        "location": stock_data[3],
        "quantity": stock_data[4],
        "cost": stock_data[5],
    }


class StockOperator:
    @staticmethod
    def get_all_stocks():
        with DBSession() as db:
            return db.query(Stock).all()

    @staticmethod
    def add_stock(data: StockIn):
        stock_found = StockOperator.get_stock_by(data.barcode)
        if not stock_found:
            last_stock_added = Barcode.get_last_stock()
            code = last_stock_added.code if last_stock_added else None
            new_code = generate_codes(code)
        else:
            new_code = stock_found.code
        data.__dict__["code"] = new_code
        new_stock = Stock(**data.__dict__)
        new_stock_created = new_stock.save()
        SR.create_running_stock(
            barcode=data.barcode,
            stock_operator=StockOperator,
        )
        return new_stock_created

    @staticmethod
    def group_all_stock_barcode():
        with DBSession() as db:
            query = db.query(
                Stock.barcode,
                Stock.code,
                Stock.specification,
                Stock.location,
                func.sum(Stock.quantity).label("total_quantity"),
                Stock.cost,
            ).group_by(Stock.barcode)
            return parse_stock_data(query.all())

    @staticmethod
    def get_grouped_stocks_with_stock_barcode(barcode: str):
        with DBSession() as db:
            query = (
                db.query(
                    Stock.barcode,
                    Stock.code,
                    Stock.specification,
                    Stock.location,
                    func.sum(Stock.quantity).label("total_quantity"),
                    Stock.cost,
                )
                .filter(Stock.barcode == barcode)
                .group_by(Stock.barcode)
            )
            return parse_stock_data(query.one_or_none())

    @staticmethod
    def get_stock_by(id_or_barcode: Union[str, int]):
        with DBSession() as db:
            return db.query(Stock).filter(Stock.id == id_or_barcode).first()

    @staticmethod
    def update_stock(stock_id: int, data: StockIn):
        values = data.__dict__
        values["updated_at"] = datetime.datetime.now(datetime.UTC)
        with DBSession() as db:
            query = db.query(Stock).filter(Stock.id == stock_id)
            query.update(values, synchronize_session=False)
            updated_instance = query.one_or_none()
            db.commit()
            SR.create_running_stock(
                barcode=data.barcode,
                stock_operator=StockOperator,
            )
            return updated_instance

    @staticmethod
    def remove_stock(stock_id: int):
        with DBSession() as db:
            stock_found = db.query(Stock).filter(Stock.id == stock_id).first()
            if not stock_found:
                raise ValueError("Stock not found")
            db.delete(stock_found)
            db.commit()
            SR.create_running_stock(
                barcode=stock_found.barcode,
                stock_operator=StockOperator,
                should_delete_quantity=True,
            )
            return True
