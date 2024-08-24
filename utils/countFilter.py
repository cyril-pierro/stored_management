from schemas.stock import StockQuery
from typing import TypeVar, Any
from utils.session import DBSession


DB_MODEL = TypeVar("T")
DB_QUERY = TypeVar("T")


class StockFilter:
    def __init__(
        self,
        query_params: StockQuery,
        db_model: DB_MODEL = None,
        query_to_use: DB_QUERY = None,
    ):
        self.db_model = db_model
        self.query_params = query_params
        self.query_to_use = query_to_use

    def apply(self) -> list[dict[str, Any]]:
        if not self.query_to_use:
            with DBSession() as db:
                query = db.query(self.db_model)
            if self.query_params.sorted:
                query = query.order_by(self.db_model.id)

            else:
                query = query.order_by(self.db_model.id.desc())
        else:
            query = self.query_to_use

        if self.query_params.from_value:
            query = query.offset(
                0
                if self.query_params.from_value - 1 <= 0
                else self.query_params.from_value - 1
            )
        if self.query_params.to_value:
            query = query.limit(
                self.query_params.to_value
                if self.query_params.from_value - 1 <= 0
                else self.query_params.to_value - self.query_params.from_value + 1
            )
        return query.all()
