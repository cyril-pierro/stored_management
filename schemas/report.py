from pydantic import BaseModel


class ErmReportOut(BaseModel):
    id: int
    date: str
    event_number: int
    part_code: str
    part_type: str
    part_description: str
    quantity: int
    erm_code: str


class ErmQuantityOut(BaseModel):
    erm_code: str
    quantity: int


class MonthlyCollectionOut(BaseModel):
    date: int
    num_of_orders: int
    quantity: int