from models.stock import Stock
from schemas.stock import StockIn
from utils.session import DBSession
from utils.generate import generate_codes
from typing import Union
import datetime
from sqlalchemy import func


class StockOperator:
    @staticmethod
    def get_all_stocks():
        with DBSession() as db:
            return db.query(Stock).all()

    @staticmethod
    def add_stock(data: StockIn):
        stock_found = StockOperator.get_stock_by(data.barcode)
        if not stock_found:
            last_stock_added = Stock.get_last_stock()
            code = last_stock_added.code if last_stock_added else None
            new_code = generate_codes(code)
        else:
            new_code = stock_found.code
        data.__dict__["code"] = new_code
        new_stock = Stock(**data.__dict__)
        return new_stock.save()
    
    @staticmethod
    def group_all_stock_barcode():
        with DBSession() as db:
            query = db.query(
                Stock.barcode, func.sum(Stock.quantity).label("total_quantity")
            ).group_by(Stock.barcode)
            return query.all()
    
    @staticmethod
    def get_grouped_stocks_with_stock_barcode(barcode: str):
        with DBSession() as db:
            query = (
                db.query(
                    Stock.barcode,
                    func.sum(Stock.quantity).label("total_quantity"),
                )
                .filter(Stock.barcode == barcode)
                .group_by(Stock.barcode)
            )
            return query.one_or_none()

    @staticmethod
    def get_stock_by(id_or_barcode: Union[str, int]):
        with DBSession() as db:
            if isinstance(id_or_barcode, str):
                stock_found = (
                    db.query(Stock).filter(Stock.barcode == id_or_barcode).first()
                )
            else:
                stock_found = db.query(Stock).filter(Stock.id == id_or_barcode).first()
            return stock_found

    @staticmethod
    def update_stock(stock_id: int, data: StockIn):
        values = data.__dict__
        values["updated_at"] = datetime.datetime.now(datetime.UTC)
        with DBSession() as db:
            query = db.query(Stock).filter(Stock.id == stock_id)
            query.update(values, synchronize_session=False)
            updated_instance = query.one_or_none()
            db.commit()
            return updated_instance

    @staticmethod
    def remove_stock(stock_id: int):
        with DBSession() as db:
            stock_found = db.query(Stock).filter(Stock.id == stock_id).first()
            if not stock_found:
                raise ValueError("Stock not found")
            db.delete(stock_found)
            return True
