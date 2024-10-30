from fastapi import APIRouter, Depends, Query

from controllers.auth import Auth
from controllers.operations import StaffOperator
from controllers.order import OrderOperator
from controllers.stock import StockOperator, ScanStock
from controllers.stock_adjustment import StockAdjustmentOperator as SA
from controllers.stock_out import StockOutOperator
from controllers.stock_running import StockRunningOperator as SR
from error import AppError
from schemas.operations import SuccessOut
from schemas.order import OrderOut
from schemas.stock import (
    Barcode,
    RunningStockOut,
    StockAdjustmentGroupOut,
    StockAdjustmentIn,
    StockAdjustmentOut,
    StockIn,
    StockOut,
    StockOutOut,
    UpdateStockAdjustmentIn,
    StockQuery,
    BarcodeIn,
    UpdateIn,
    CostEvaluationOut
)
from utils.common import bearer_schema
from typing import Optional


PERMISSION_ERROR = "You do not have permission to perform this operation"
op_router = APIRouter()


@op_router.get("/barcodes", response_model=list[Barcode])
async def get_available_barcodes(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(
        staff_id=staff_id
    ) or StaffOperator.has_engineer_permission(staff_id):
        return StockOperator.get_all_barcodes()
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@op_router.post("/barcode", response_model=Barcode)
async def add_scan_stock(
    data: BarcodeIn,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(
        staff_id=staff_id
    ):
        return ScanStock.add_barcode(data)
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@op_router.get("/barcode/{barcode_id}", response_model=Barcode)
async def get_scan_stock(
    barcode_id: int,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(
        staff_id=staff_id
    ):
        return ScanStock.get_barcode(barcode_id)
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@op_router.delete("/barcode/{barcode_id}", response_model=SuccessOut)
async def delete_scan_stock(
    barcode_id: int,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(
        staff_id=staff_id
    ):
        ScanStock.delete_barcode(barcode_id)
        return {"message": "Scan code deleted successfully"}
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@op_router.put("/barcode/{barcode_id}", response_model=Barcode)
async def edit_scan_stock(
    barcode_id: int, data: UpdateIn,
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(
        staff_id=staff_id
    ):
        return ScanStock.edit_barcode(barcode_id, data)
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@op_router.get("/stock/{id}", response_model=StockOut)
async def get_stock_by_id(id: int, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    stock = StockOperator.get_stock_by(id)
    if not stock:
        raise ValueError("Stock not found")
    return stock


@op_router.get("/stock/barcode/{barcode}", response_model=StockOut)
async def get_stock_by_barcode(
    barcode: str, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    stock = StockOperator.get_stock_by(barcode)
    if not stock:
        raise ValueError(f"Stock with barcode {barcode} not found")
    return stock.json()


@op_router.get("/stock-in/history", response_model=list[StockOut])
async def get_all_stocks_delivered(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return StockOperator.get_all_stocks()


@op_router.get("/stock-in", response_model=list[Barcode])
async def get_all_stocks_per_barcode(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(
        staff_id=staff_id
    ) or StaffOperator.has_engineer_permission(staff_id):
        return StockOperator.group_all_stock_barcode()
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@op_router.get("/stock-in/{barcode}", response_model=Barcode)
async def get_all_stocks_per_barcode_with_specific_barcode(
    barcode: str, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    value = StockOperator.get_grouped_stocks_with_stock_barcode(barcode)
    if not value:
        raise ValueError("Could not find stock with barcode")
    return value


@op_router.post("/stock", response_model=StockOut)
async def create_stock(data: StockIn, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return StockOperator.add_stock(data, staff_id)


@op_router.put("/stock/{id}", response_model=StockOut)
async def update_stock_info(
    id: int, data: StockIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return StockOperator.update_stock(id, data, staff_id)


@op_router.delete("/stock/{id}", response_model=SuccessOut)
async def delete_stock(id: int, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    status = StockOperator.remove_stock(id)
    if status:
        return {"message": "Stock has been removed from the store"}


@op_router.get("/stock-out/history", response_model=list[StockOutOut])
async def get_stock_outs(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return StockOutOperator.get_all_stocks()


@op_router.get("/stock-out", response_model=list[Barcode])
async def get_stock_out_group_data(
    access_token: str = Depends(bearer_schema),
    query_params: StockQuery = Depends(),
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return StockOutOperator.group_all_stock_ids_data(query_params)


@op_router.get("/stock-out/{stock_id}", response_model=Barcode)
async def get_stock_out_group_data_by_id(
    stock_id: int, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    value = StockOutOperator.get_group_all_stock_ids_data_by_stock_id(stock_id)
    if not value:
        raise ValueError("Stock out record not found")
    return value


@op_router.post(
    "/stock-adjustment/{barcode}",
    response_model=SuccessOut,
)
async def create_stock_adjustment(
    barcode: str, data: StockAdjustmentIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    status = SA.create_stock_adjustment(barcode, data, staff_id)
    if status:
        return {"message": "Stock adjustment created successfully"}

@op_router.get("/stock-adjustment/history", response_model=list[StockAdjustmentOut])
async def get_stock_adjustment_history(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return SA.get_all_stock_adjustments()


@op_router.get("/stock-adjustment", response_model=list[StockAdjustmentGroupOut])
async def get_stock_adjustment_grouped(
    access_token: str = Depends(bearer_schema),
    query_params: StockQuery = Depends(),
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return SA.group_all_stock_adjustments_for_stocks(query_params)


@op_router.get("/stock-adjustment/{barcode}", response_model=StockAdjustmentGroupOut)
async def get_stock_adjustment_grouped_by_stock_id(
    barcode: str, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    value = SA.get_grouped_stock_adjustments_by_barcode(barcode)
    if not value:
        raise ValueError("Stock Adjustment record does not exist")
    return value


@op_router.put("/stock-adjustment/{id}", response_model=StockAdjustmentOut)
async def edit_stock_adjustment(
    id: int, data: UpdateStockAdjustmentIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return SA.update_stock_adjustment(id, data, staff_id)


@op_router.delete("/stock-adjustment/{id}", response_model=SuccessOut)
async def delete_stock_adjustment(id: int, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    status = SA.delete_stock_adjustment(id)
    if status:
        return {"message": "Stock adjustment deleted successfully"}


@op_router.get("/stock-running", response_model=list[RunningStockOut])
async def get_running_stocks(
    access_token: str = Depends(bearer_schema),
    query_params: StockQuery = Depends(),
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(
        staff_id=staff_id
    ) or StaffOperator.has_engineer_permission(staff_id):
        return SR.get_all_running_stocks(query_params=query_params)
    raise AppError(message=PERMISSION_ERROR, status_code=401)


@op_router.get("/orders", response_model=list[OrderOut])
async def get_all_orders(
    from_: Optional[str] = Query(None),
    to_: Optional[str] = Query(None),
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return OrderOperator.get_all_orders(from_=from_, to_=to_)


@op_router.get("/cost-evaluation", response_model=list[CostEvaluationOut])
async def get_all_cost_evaluation(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return StockOperator.get_all_cost_evaluation_data()

