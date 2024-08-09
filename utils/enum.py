from enum import Enum


class RunningStockStatus(Enum):
    available = "available"
    re_order = "reorder"


class OrderStatus(Enum):
    part_not_available = "part_not_available"
    part_available = "part_available"
