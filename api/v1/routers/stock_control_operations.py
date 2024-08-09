from fastapi import APIRouter

from controllers.stock import StockOperator
from controllers.stock_out import StockOutOperator
from schemas.stock import StockIn

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
    print(StockOperator.group_all_stock_barcode())
    return True


@op_router.get("/stock-in/{barcode}")
def get_all_stocks_per_barcode_with_barcode_of(barcode: str):
    return StockOperator.get_grouped_stocks_with_stock_barcode(barcode)


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
        raise ValueError(f"Stock out record not found for stock with id: {stock_id}")
    return value

