from typing import Any


class ReportParser:
    @staticmethod
    def convert_engineers_to_departments_data(data: list[dict[Any, str]]):
        if len(data) == 0:
            return data
        return [
            {
                "department": value[0].name,
                "number_of_engineers": value[1]
            } for value in data
        ]
    
    @staticmethod
    def convert_department_adjustment_orders_data(data: list[dict[Any, str]]):
        if len(data) == 0:
            return data
        return [
            {
                "department": value[0],
                "number_of_adjustments":  0 if not value[1] else value[1],
                "number_of_orders": 0 if not value[2] else value[2]
            }
            for value in data
        ]
    
    @staticmethod
    def convert_number_and_quantity_orders_data(data: list[dict[Any, str]]):
        if len(data) == 0:
            return data
        return [
            {
                "department": value[0],
                "number_of_orders":  0 if not value[1] else value[1],
                "quantity_of_orders": 0 if not value[2] else value[2]
            }
            for value in data
        ]