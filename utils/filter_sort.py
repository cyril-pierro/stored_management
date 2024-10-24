from typing import List, Type, TypeVar

from fastapi import Query
from fastapi_pagination import paginate
from sqlalchemy import String, and_, inspect, sql
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

T = TypeVar("T")


class FilterSort:
    def __init__(
        self, db_model: Type[T], request_query_params: dict, db: Session = None
    ):
        self.db_model = db_model
        self.db_model_inspect = inspect(db_model)
        self.request_query_params = request_query_params
        self.db = db

    # get column name from param_name
    def get_column_name(self, param_name: str) -> tuple[str, str]:
        if param_name.endswith("_min"):
            return param_name[:-4], "min"  # Remove the "_min" suffix
        elif param_name.endswith("_max"):
            return param_name[:-4], "max"  # Remove the "_max" suffix
        else:
            return param_name, "main"

    def apply_filters(self, query: Query) -> Query:
        filters = []
        for param_name, param_value in self.request_query_params.items():
            column_name, column_type = self.get_column_name(param_name)

            for column in self.db_model_inspect.columns:
                if column.name == column_name:
                    if column_type == "min":
                        param_value = datetime.strptime(
                            param_value, "%Y-%m-%d") + timedelta(hours=0, minutes=0, seconds=0)
                        query = query.filter(
                            getattr(self.db_model, column_name) >= param_value
                        )
                    elif column_type == "max":
                        param_value = datetime.strptime(
                            param_value, "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)

                        query = query.filter(
                            getattr(self.db_model, column_name) <= param_value
                        )
                    elif type(column.type) == String:
                        # If the column is a string type, use LIKE for filtering
                        filters.append(
                            getattr(self.db_model, column_name).ilike(
                                f"%{param_value}%"
                            )
                        )
                    elif type(column.type) == sql.sqltypes.Enum:
                        query = query.filter(
                            getattr(self.db_model,
                                    column_name) == param_value.name
                        )

                    else:
                        filters.append(
                            getattr(self.db_model, column_name)
                            == str(param_value).lower()
                        )

        if filters:
            query = query.filter(and_(*filters))

        return query

    def apply_sorting(self, query: Query) -> Query:
        if sort_param := self.request_query_params.get("sort"):
            sort_columns = sort_param.split(",")
            for col in sort_columns:
                if col.startswith("-"):
                    query = query.order_by(
                        getattr(self.db_model, col[1:]).desc())
                else:
                    query = query.order_by(getattr(self.db_model, col))
        return query

    # handle None filter and sort values
    def handle_none_filter_and_sort(self):
        temporal_dict: dict = self.request_query_params.copy()

        for param_name, param_value in temporal_dict.items():
            if param_value is None:
                del self.request_query_params[param_name]

    def filter_and_sort(self) -> List[T]:
        query = self.db.query(self.db_model)

        self.handle_none_filter_and_sort()

        # check is query dict is empty
        if self.request_query_params:
            query = self.apply_filters(query)
            query = self.apply_sorting(query)

        result = query.all()
        return paginate(result)
