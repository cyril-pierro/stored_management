from sqlalchemy import func

from models.stock_out import StockOut
from utils.session import DBSession


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
            return query.all()

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
            return query.one_or_none()
