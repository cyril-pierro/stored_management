from fastapi import APIRouter, BackgroundTasks, Depends

from controllers.auth import Auth
from controllers.operations import StaffOperator
from controllers.order import OrderOperator as OO
from error import AppError
from schemas.order import OrderIn, OrderOut, OrdersDoneOut
from schemas.stock import RunningStockAvailabilityOut as RSO
from utils.common import bearer_schema

PERMISSION_ERROR = "You do not have permission to perform this operation"
op_router = APIRouter()


@op_router.get("/stock/{barcode}/available", response_model=RSO)
async def check_if_part_is_available(
    barcode: str, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_engineer_permission(staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return OO.check_if_order_is_available(barcode)


@op_router.get("/orders/done", response_model=OrdersDoneOut)
async def get_number_of_orders_done(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_engineer_permission(staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return {"number": OO.get_number_of_orders()}


@op_router.post("/stock/{barcode}/collect", response_model=OrderOut)
async def buy_or_collect_stock_from_store(
    barcode: str,
    data: OrderIn,
    background_tasks: BackgroundTasks,
    access_token: str = Depends(bearer_schema),
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_engineer_permission(staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return OO.create_order_for_stock_with(
        barcode=barcode, data=data, user_id=staff_id, background_task=background_tasks
    )
