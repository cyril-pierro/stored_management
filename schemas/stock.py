from pydantic import BaseModel


class StockIn(BaseModel):
    barcode: str
    specification: str
    location: str
    quantity: int
    cost: float


class StockOut(StockIn):
    id: int
    code: str


class StockAdjustmentIn(BaseModel):
    department_id: int
    quantity: int


class UpdateStockAdjustmentIn(StockAdjustmentIn):
    barcode: str
