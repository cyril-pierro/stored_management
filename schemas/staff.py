from pydantic import BaseModel, Field


class StaffIn(BaseModel):
    staff_id_number: str = Field(alias="engineer_id")
    name: str
    job_id: int
    department_id: int


class StaffOut(BaseModel):
    id: int
    name: str


class UpdateStaffIn(BaseModel):
    name: str
