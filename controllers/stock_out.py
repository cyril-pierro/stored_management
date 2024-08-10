from typing import Any, Union

from sqlalchemy import func

from models.stock_out import StockOut
from utils.session import DBSession


def parse_stock_out_data(data: Union[Any, list, None]):
    if not data:
        return data
    if isinstance(data, list):
        return [{"stock_id": i[0], "quantity": i[1]} for i in data]
    return {"stock_id": data[0], "quantity": data[1]}


class StockOutOperator:
    @staticmethod
    def get_all_stocks():
        with DBSession() as db:
            return db.query(StockOut).all()

    @staticmethod
    def group_all_stock_ids_data():
        with DBSession() as db:
            query = db.query(
                StockOut.stock_id, func.sum(StockOut.quantity).label("total_quantity")
            ).group_by(StockOut.stock_id)
            return parse_stock_out_data(query.all())

    @staticmethod
    def get_group_all_stock_ids_data_by_stock_id(stock_id: int):
        with DBSession() as db:
            query = (
                db.query(
                    StockOut.stock_id,
                    func.sum(StockOut.quantity).label("total_quantity"),
                )
                .filter(StockOut.stock_id == stock_id)
                .group_by(StockOut.stock_id)
            )
            return parse_stock_out_data(query.one_or_none())
