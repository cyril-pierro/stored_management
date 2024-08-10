from fastapi import APIRouter

from controllers.order import OrderOperator as OO
from schemas.order import OrderIn

op_router = APIRouter()


@op_router.get("/stock/{barcode}/available/")
def check_if_part_is_available(barcode: str):
    return OO.check_if_order_is_available(barcode)


@op_router.get("/orders/done")
def get_number_of_orders_done():
    return {"number": OO.get_number_of_orders()}


@op_router.post("/stock/{barcode}/collect")
def buy_or_collect_stock_from_store(data: OrderIn):
    return OO.create_order(data)
