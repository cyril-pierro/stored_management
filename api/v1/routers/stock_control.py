from fastapi import APIRouter

from controllers.order import OrderOperator
from controllers.stock import StockOperator
from controllers.stock_adjustment import StockAdjustmentOperator as SA
from controllers.stock_out import StockOutOperator
from controllers.stock_running import StockRunningOperator as SR
from schemas.stock import StockAdjustmentIn, StockIn, UpdateStockAdjustmentIn

op_router = APIRouter()


@op_router.get("/stock/{id}")
def get_stock_by_id(id: int):
    stock = StockOperator.get_stock_by(id)
    if not stock:
        raise ValueError("Stock not found")
    return stock.json()


@op_router.get("/stock/barcode/{barcode}")
def get_stock_by_barcode(barcode: str):
    stock = StockOperator.get_stock_by(barcode)
    if not stock:
        raise ValueError(f"Stock with barcode {barcode} not found")
    return stock.json()


@op_router.get("/stock-in/history")
def get_all_stocks_delivered():
    return StockOperator.get_all_stocks()


@op_router.get("/stock-in")
def get_all_stocks_per_barcode():
    return StockOperator.group_all_stock_barcode()


@op_router.get("/stock-in/{barcode}")
def get_all_stocks_per_barcode_with_specific_barcode(barcode: str):
    value = StockOperator.get_grouped_stocks_with_stock_barcode(barcode)
    if not value:
        raise ValueError("Could not find stock with barcode")
    return value


@op_router.post("/stock")
def create_stock(data: StockIn):
    return StockOperator.add_stock(data).json()


@op_router.put("/stock/{id}")
def update_stock_info(id: int, data: StockIn):
    return StockOperator.update_stock(id, data)


@op_router.delete("/stock/{id}")
def delete_stock(id: int):
    status = StockOperator.remove_stock(id)
    if status:
        return {"message": "Stock has been removed from the store"}


@op_router.get("/stock-out/history")
def get_stock_outs():
    return StockOutOperator.get_all_stocks()


@op_router.get("/stock-out")
def get_stock_out_group_data():
    return StockOutOperator.group_all_stock_ids_data()


@op_router.get("/stock-out/{stock_id}")
def get_stock_out_group_data_by_id(stock_id: int):
    value = StockOutOperator.get_group_all_stock_ids_data_by_stock_id(stock_id)
    if not value:
        raise ValueError("Stock out record not found")
    return value


@op_router.post("/stock-adjustment/{barcode}")
def create_stock_adjustment(barcode: str, data: StockAdjustmentIn):
    return SA.create_stock_adjustment(barcode, data).json()


@op_router.get("/stock-adjustment/history")
def get_stock_adjustment_history():
    return SA.get_all_stock_adjustments()


@op_router.get("/stock-adjustment")
def get_stock_adjustment_grouped():
    return SA.group_all_stock_adjustments_for_stocks()


@op_router.get("/stock-adjustment/{barcode}")
def get_stock_adjustment_grouped_by_stock_id(barcode: str):
    value = SA.get_grouped_stock_adjustments_by_barcode(barcode)
    if not value:
        raise ValueError("Stock Adjustment record does not exist")
    return value


@op_router.put("/stock-adjustment/{id}")
def edit_stock_adjustment(id: int, data: UpdateStockAdjustmentIn):
    return SA.update_stock_adjustment(id, data).json()


@op_router.get("/stock-running")
def get_running_stocks():
    return SR.get_all_running_stocks()


@op_router.get("/orders")
def get_all_orders():
    return OrderOperator.get_all_orders()
