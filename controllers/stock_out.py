from typing import Any, Union

from sqlalchemy import func

from models.barcode import Barcode
from models.stock_out import StockOut
from utils.session import DBSession
from schemas.stock import StockQuery
from utils.countFilter import StockFilter


def parse_stock_out_data(data: Union[Any, list, None]):
    if not data:
        return data
    if isinstance(data, list):
        return [
            {
                "id": i[0].id,
                "barcode": i[0].barcode,
                "location": i[0].location,
                "specification": i[0].specification,
                "code": i[0].code,
                # "cost": i[0].cost,
                "quantity": i[1],
            }
            for i in data
        ]
    return {
        "id": data[0].id,
        "barcode": data[0].barcode,
        "location": data[0].location,
        "specification": data[0].specification,
        "code": data[0].code,
        "quantity": data[1],
    }


class StockOutOperator:
    @staticmethod
    def get_all_stocks():
        with DBSession() as db:
            return db.query(StockOut).order_by(StockOut.id.desc()).all()

    @staticmethod
    def create_stock_out(barcode_id: int, quantity: int, order_id: int = None):
        new_stock_out = StockOut(
            barcode_id=barcode_id,
            quantity=quantity,
            order_id=order_id,
        )
        return new_stock_out.save()

    @staticmethod
    def group_all_stock_ids_data(query_params: StockQuery):
        with DBSession() as db:
            query = (
                db.query(Barcode, func.sum(StockOut.quantity).label("total_quantity"))
                .join(StockOut, Barcode.id == StockOut.barcode_id)
                .group_by(StockOut.barcode_id, Barcode.id)
            )
            filter_instance = StockFilter(query_params, query_to_use=query)
            return parse_stock_out_data(filter_instance.apply())

    @staticmethod
    def get_group_all_stock_ids_data_by_stock_id(barcode: str):
        with DBSession() as db:
            query = (
                db.query(
                    Barcode,
                    func.sum(StockOut.quantity).label("total_quantity"),
                )
                .join(StockOut, Barcode.id == StockOut.barcode_id)
                .filter(Barcode.barcode == barcode)
                .group_by(StockOut.barcode_id, Barcode.id)
            )
            return parse_stock_out_data(query.one_or_none())
