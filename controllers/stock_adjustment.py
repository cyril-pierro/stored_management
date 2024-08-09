from models.stock_adjustment import StockAdjustment
from controllers.stock import StockOperator as so
from utils.session import DBSession
from schemas.stock import StockAdjustmentIn
from sqlalchemy import func


class StockAdjustmentOperator:
    @staticmethod
    def get_all_stock_adjustments():
        with DBSession() as db:
            return db.query(StockAdjustment).all()
    
    @staticmethod
    def create_stock_adjustment(stock_id: int, data: StockAdjustmentIn):
        if not so.get_stock_by(stock_id):
            raise ValueError("Stock not found to perform adjustment")
        values = data.__dict__
        values['stock_id'] = stock_id
        stock_adj = StockAdjustment(**values)
        return stock_adj.save()
    
    @staticmethod
    def group_all_stock_adjustments_for_stocks():
        with DBSession() as db:
            query = db.query(
                StockAdjustment.stock_id, func.sum(StockAdjustment.quantity).label("total_quantity")
            ).group_by(StockAdjustment.stock_id)
            return query.all()
    
    @staticmethod
    def get_grouped_stock_adjustments_by_stock_id(stock_id: int):
        with DBSession() as db:
            query = (
                db.query(
                    StockAdjustment.stock_id,
                    func.sum(StockAdjustment.quantity).label("total_quantity"),
                )
                .filter(StockAdjustment.stock_id == stock_id)
                .group_by(StockAdjustment.stock_id)
            )
            return query.one_or_none()

    