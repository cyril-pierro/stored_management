from typing import Any


class ReportParser:
    @staticmethod
    def convert_engineers_to_departments_data(data: list[dict[Any, str]]):
        if not data:
            return data
        return [
            {
                "department": value[0].name,
                "number_of_engineers": value[1]
            } for value in data
        ]

    @staticmethod
    def convert_department_adjustment_orders_data(data: list[dict[Any, str]]):
        if not data:
            return data
        return [
            {
                "department": value[0],
                "number_of_adjustments":  value[1] or 0,
                "number_of_orders": value[2] or 0,
            }
            for value in data
        ]

    @staticmethod
    def convert_number_and_quantity_orders_data(data: list[dict[Any, str]]):
        if not data:
            return data
        return [
            {
                "department": value[0],
                "number_of_orders":  value[1] or 0,
                "quantity_of_orders": value[2] or 0,
                "total_cost": max(value[3] or 0, 0) * max(value[2] or 0, 0),
            }
            for value in data
        ]
