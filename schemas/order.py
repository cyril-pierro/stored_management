from pydantic import BaseModel

from utils.enum import RunningStockStatus


class OrderIn(BaseModel):
    job_number: str
    part_name: str
    quantity: int
    status: RunningStockStatus
