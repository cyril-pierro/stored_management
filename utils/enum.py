from enum import Enum


class RunningStockStatus(Enum):
    available = "available"
    re_order = "re_order"


class OrderStatus(Enum):
    part_not_available = "part_not_available"
    part_available = "part_available"
