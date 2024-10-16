from enum import Enum


class RunningStockStatus(Enum):
    available = "available"
    re_order = "re_order"


class OrderStatus(Enum):
    part_not_available = "part_not_available"
    part_available = "part_available"


class RolesStatus(Enum):
    engineer = "engineer"
    stock_controller = "stock_controller"


class PurchaseOrderStates(Enum):
    draft = "draft"
    sent = "sent"
    validate = "validate"